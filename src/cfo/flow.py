from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.core.tools.registry import ToolRegistry, ToolSpec
from src.core.tools.runner import ToolRunner
from src.cfo import tools as cfo_tools
from src.experts.cfo_subagents.consulting_agent import CFOConsultingAgent
from src.experts.cfo_subagents.computation_agent import CFOComputationAgent
from src.experts.cfo_subagents.knowledge_qa_agent import CFOKnowledgeQAAgent
from src.experts.cfo_subagents.text_analysis_agent import CFOTextAnalysisAgent
from src.finance import (
    amortization_schedule,
    break_even_quantity,
    cagr,
    fv,
    growth_rate,
    irr,
    npv,
    pv,
    solve_linear,
    solve_quadratic,
)
from src.llm.client import LLMClient
from src.cfo.subagents.document_parser import CFODocumentParser
from src.cfo.subagents.indicator_engine import CFOIndicatorEngine
from src.cfo.subagents.intent_router import CFOIntentRouter
from src.cfo.subagents.section_orchestrator import CFOSectionOrchestrator
from src.cfo.subagents.snippet_retriever import CFOSnippetRetriever
from src.models.request_response import ExpertRequest


@dataclass(frozen=True)
class CFOFlowConfig:
    max_snippets: int = 5
    max_chars_per_snippet: int = 280
    tool_timeout_sec: float = 20.0
    enable_consulting_agent: bool = True
    enable_llm: bool = False


class CFOFlow:
    def __init__(self, *, config: Optional[CFOFlowConfig] = None) -> None:
        self._config = config or CFOFlowConfig()
        registry = ToolRegistry()
        registry.register(ToolSpec(name="cfo.parse_financial_document", fn=cfo_tools.parse_financial_document, timeout_sec=self._config.tool_timeout_sec))
        registry.register(ToolSpec(name="cfo.extract_financials", fn=cfo_tools.extract_financials, timeout_sec=self._config.tool_timeout_sec))
        registry.register(ToolSpec(name="cfo.extract_financials_series", fn=cfo_tools.extract_financials_series, timeout_sec=self._config.tool_timeout_sec))
        registry.register(ToolSpec(name="cfo.compute_financial_indicators", fn=cfo_tools.compute_financial_indicators, timeout_sec=self._config.tool_timeout_sec))
        registry.register(ToolSpec(name="cfo.compute_period_changes", fn=cfo_tools.compute_period_changes, timeout_sec=self._config.tool_timeout_sec))
        registry.register(ToolSpec(name="cfo.retrieve_document_snippets", fn=cfo_tools.retrieve_document_snippets, timeout_sec=self._config.tool_timeout_sec))
        registry.register(ToolSpec(name="finance.growth_rate", fn=growth_rate, timeout_sec=self._config.tool_timeout_sec))
        registry.register(ToolSpec(name="finance.cagr", fn=cagr, timeout_sec=self._config.tool_timeout_sec))
        registry.register(ToolSpec(name="finance.npv", fn=npv, timeout_sec=self._config.tool_timeout_sec))
        registry.register(ToolSpec(name="finance.irr", fn=irr, timeout_sec=self._config.tool_timeout_sec))
        registry.register(ToolSpec(name="finance.pv", fn=pv, timeout_sec=self._config.tool_timeout_sec))
        registry.register(ToolSpec(name="finance.fv", fn=fv, timeout_sec=self._config.tool_timeout_sec))
        registry.register(ToolSpec(name="finance.amortization", fn=amortization_schedule, timeout_sec=self._config.tool_timeout_sec))
        registry.register(ToolSpec(name="finance.break_even", fn=break_even_quantity, timeout_sec=self._config.tool_timeout_sec))
        registry.register(ToolSpec(name="math.solve_linear", fn=solve_linear, timeout_sec=self._config.tool_timeout_sec))
        registry.register(ToolSpec(name="math.solve_quadratic", fn=solve_quadratic, timeout_sec=self._config.tool_timeout_sec))

        runner = ToolRunner(registry)
        self._tool_runner = runner
        self._router = CFOIntentRouter()
        self._parser = CFODocumentParser(runner)
        self._indicator_engine = CFOIndicatorEngine(runner)
        self._snippet_retriever = CFOSnippetRetriever(runner)
        self._sections = CFOSectionOrchestrator()
        self._computation = CFOComputationAgent()
        self._text_analysis = CFOTextAnalysisAgent()
        self._knowledge_qa = CFOKnowledgeQAAgent()
        self._consulting = CFOConsultingAgent() if self._config.enable_consulting_agent else None
        self._llm = LLMClient() if self._config.enable_llm else None

    async def run(self, request: ExpertRequest) -> Dict[str, Any]:
        extra_params = request.extra_params or {}
        task_type = request.task_type or "cfo_chat"
        file_path = extra_params.get("file_path")
        file_paths = extra_params.get("file_paths")
        file_paths = file_paths if isinstance(file_paths, list) else None
        file_tags_by_path = extra_params.get("file_tags_by_path")
        file_tags_by_path = file_tags_by_path if isinstance(file_tags_by_path, dict) else None
        business_context = extra_params.get("business_context")
        business_context = business_context if isinstance(business_context, dict) else None
        valid_file_paths: Optional[List[str]] = None
        if file_paths:
            tmp: List[str] = []
            for p in file_paths:
                if isinstance(p, str) and p.strip():
                    tmp.append(p)
            valid_file_paths = tmp or None
        financials = extra_params.get("financials")
        financials = financials if isinstance(financials, dict) else None

        intent = self._router.route(text=request.text or "", task_type=task_type)
        parsed_data = await self._parser.parse(file_path, file_paths=valid_file_paths)
        extracted_financials = None
        financials_series: List[Dict[str, Any]] = []
        period_changes = None

        if parsed_data or financials:
            series_payload = await self._tool_runner.run(
                "cfo.extract_financials_series",
                parsed_data=parsed_data,
                financials=financials,
            )
            s = series_payload.get("series") if isinstance(series_payload, dict) else None
            financials_series = s if isinstance(s, list) else []
            selected = series_payload.get("selected") if isinstance(series_payload, dict) else None
            if financials is None and isinstance(selected, dict):
                v = selected.get("values")
                if isinstance(v, dict):
                    financials = v
                extracted_financials = selected

            if len(financials_series) >= 2:
                period_changes = await self._tool_runner.run("cfo.compute_period_changes", series=financials_series)

        indicators = await self._indicator_engine.compute(parsed_data, financials=financials)
        per_file_indicators = None
        if isinstance(parsed_data, dict) and isinstance(parsed_data.get("documents"), list):
            items: List[Dict[str, Any]] = []
            for d in parsed_data.get("documents") or []:
                if not isinstance(d, dict):
                    continue
                p = d.get("file_path")
                pd = d.get("parsed")
                if not isinstance(p, str) or not p.strip():
                    continue
                extracted = await self._tool_runner.run("cfo.extract_financials", parsed_data=pd)
                v = extracted.get("values") if isinstance(extracted, dict) else None
                v = v if isinstance(v, dict) else None
                out = await self._indicator_engine.compute(pd, financials=v)
                purpose = None
                if file_tags_by_path and p in file_tags_by_path:
                    tag = file_tags_by_path.get(p)
                    if isinstance(tag, dict):
                        purpose = tag.get("purpose")
                    elif isinstance(tag, str):
                        purpose = tag
                items.append({"file_path": p, "purpose": purpose, "indicators": out, "financials_extracted": extracted})
            per_file_indicators = items or None
        snippets = await self._snippet_retriever.retrieve(
            query=request.text or "",
            parsed_data=parsed_data,
            file_tags_by_path=file_tags_by_path,
            max_snippets=self._config.max_snippets,
            max_chars_per_snippet=self._config.max_chars_per_snippet,
        )
        snippets_by_purpose: Dict[str, List[Dict[str, Any]]] = {}
        if isinstance(snippets, list):
            for s in snippets:
                if not isinstance(s, dict):
                    continue
                purpose = s.get("purpose") or "未标注"
                snippets_by_purpose.setdefault(str(purpose), []).append(s)
        capability_output = None
        sections: Dict[str, Any] = {}
        analysis_report = ""
        if intent == "finance_computation":
            out = await self._computation.run(
                query=request.text or "",
                tool_runner=self._tool_runner,
                llm=self._llm,
                extra_params=extra_params,
            )
            capability_output = {
                "capability": out.capability,
                "answer_markdown": out.answer_markdown,
                "structured": out.structured,
                "confidence": out.confidence,
                "needs_followup": out.needs_followup,
                "followup_question": out.followup_question,
            }
            analysis_report = out.answer_markdown
        elif intent == "finance_text_analysis":
            out = await self._text_analysis.run(query=request.text or "", parsed_data=parsed_data, llm=self._llm)
            capability_output = {
                "capability": out.capability,
                "answer_markdown": out.answer_markdown,
                "structured": out.structured,
                "confidence": out.confidence,
                "needs_followup": out.needs_followup,
                "followup_question": out.followup_question,
            }
            analysis_report = out.answer_markdown
        elif intent == "finance_knowledge_qa":
            out = await self._knowledge_qa.run(
                query=request.text or "",
                parsed_data=parsed_data,
                llm=self._llm,
                user_id=request.user_id or "unknown",
            )
            capability_output = {
                "capability": out.capability,
                "answer_markdown": out.answer_markdown,
                "structured": out.structured,
                "confidence": out.confidence,
                "needs_followup": out.needs_followup,
                "followup_question": out.followup_question,
            }
            analysis_report = out.answer_markdown
        else:
            enriched_extra_params = dict(extra_params)
            if valid_file_paths is not None:
                enriched_extra_params["file_paths"] = valid_file_paths
            if per_file_indicators is not None:
                enriched_extra_params["per_file_indicators"] = per_file_indicators
            if financials_series:
                enriched_extra_params["financials_series"] = financials_series
            if period_changes:
                enriched_extra_params["period_changes"] = period_changes
            sections = self._sections.build_sections(
                query=request.text or "",
                task_type=task_type,
                intent=intent,
                indicators=indicators,
                snippets=snippets,
                has_parsed_data=bool(parsed_data),
                extra_params=enriched_extra_params,
            )
            analysis_report = self._sections.assemble_report(
                query=request.text or "",
                intent=intent,
                task_type=task_type,
                indicators=indicators,
                sections=sections,
                has_parsed_data=bool(parsed_data),
                snippets_by_purpose=snippets_by_purpose,
                business_context=business_context,
            )

        consulting = None
        if self._consulting is not None:
            out = await self._consulting.run(
                query=request.text or "",
                llm=self._llm,
                context={
                    "intent": intent,
                    "indicators": indicators,
                    "snippets": snippets,
                    "sections": sections,
                    "subagents": self._sections.subagents,
                    "has_parsed_data": bool(parsed_data),
                    "file_path": file_path,
                    "file_paths": valid_file_paths,
                },
            )
            consulting = {
                "capability": out.capability,
                "answer_markdown": out.answer_markdown,
                "structured": out.structured,
                "confidence": out.confidence,
                "needs_followup": out.needs_followup,
                "followup_question": out.followup_question,
            }

        needs: List[str] = []
        needs_structured: List[Dict[str, Any]] = []

        def _add_need(*, category: str, priority: str, text: str, why: Optional[str] = None, example: Optional[str] = None) -> None:
            t = str(text or "").strip()
            if not t:
                return
            item = {
                "category": str(category or "").strip() or "其他",
                "priority": str(priority or "").strip() or "P2",
                "text": t,
                "why": str(why).strip() if isinstance(why, str) and why.strip() else None,
                "example": str(example).strip() if isinstance(example, str) and example.strip() else None,
            }
            needs_structured.append(item)
            needs.append(t)

        if isinstance(sections, dict):
            for v in sections.values():
                if not isinstance(v, dict):
                    continue
                structured = v.get("structured")
                if isinstance(structured, dict):
                    ns = structured.get("needs")
                    if isinstance(ns, list):
                        for it in ns:
                            if isinstance(it, str) and it.strip():
                                _add_need(category="材料", priority="P1", text=it.strip())
        if isinstance(consulting, dict):
            structured = consulting.get("structured")
            if isinstance(structured, dict):
                ns = structured.get("needs")
                if isinstance(ns, list):
                    for it in ns:
                        if isinstance(it, str) and it.strip():
                            _add_need(category="材料", priority="P1", text=it.strip())

        if (not parsed_data and not financials) or (isinstance(indicators, dict) and indicators.get("is_mock_data")):
            _add_need(
                category="财务数据",
                priority="P0",
                text="上传财务报表（至少利润表/资产负债表/现金流量表之一）或提供 extra_params.financials",
                why="没有可计算的核心财务数据时，结论只能基于假设，无法用于决策",
            )
            _add_need(
                category="口径",
                priority="P0",
                text="明确期间、合并范围、单位与口径（含税/不含税、权责/收付）",
                why="口径不一致会导致拆分与对比结论失真",
            )

        if business_context:
            period = str(business_context.get("period") or "").strip()
            scope = str(business_context.get("scope") or "").strip()
            include_allocations = bool(business_context.get("include_allocations", True))
            allocation_rules = str(business_context.get("allocation_rules") or "").strip()
            if not period:
                _add_need(category="口径", priority="P1", text="补充分析期间（例如：2024Q1-2025Q2 或 2023-2025）")
            if not scope:
                _add_need(category="口径", priority="P1", text="补充口径/范围（合并/母公司、含税/不含税、权责/收付、单位）")
            if include_allocations and not allocation_rules:
                _add_need(category="分摊", priority="P0", text="补充费用分摊规则（销售/研发/管理的分摊口径与规则）", why="缺少分摊规则会直接影响子业务损益结论与可比性")

        uniq_needs: List[str] = []
        seen = set()
        for n in needs:
            if n not in seen:
                seen.add(n)
                uniq_needs.append(n)

        needs_followup = bool(uniq_needs) or (bool(consulting.get("needs_followup")) if isinstance(consulting, dict) else False)

        evidence_md_parts: List[str] = []
        if isinstance(snippets_by_purpose, dict) and snippets_by_purpose:
            evidence_md_parts.append("\n\n## 材料依据（按用途）\n")
            for purpose in sorted(list(snippets_by_purpose.keys())):
                rows = snippets_by_purpose.get(purpose)
                if not isinstance(rows, list) or not rows:
                    continue
                evidence_md_parts.append(f"\n### {purpose}\n")
                shown = 0
                for s in rows:
                    if shown >= 3:
                        break
                    if not isinstance(s, dict):
                        continue
                    snippet = str(s.get("snippet") or "").strip()
                    if not snippet:
                        continue
                    fp = str(s.get("file_path") or "").strip()
                    if fp:
                        evidence_md_parts.append(f"- {snippet}（{fp.split('/')[-1]}）")
                    else:
                        evidence_md_parts.append(f"- {snippet}")
                    shown += 1
        evidence_md = "\n".join(evidence_md_parts).strip()
        if evidence_md:
            analysis_report = (analysis_report or "").rstrip() + "\n\n" + evidence_md

        return {
            "intent": intent,
            "indicators": indicators,
            "analysis_report": analysis_report,
            "has_parsed_data": bool(parsed_data),
            "file_path": file_path,
            "file_paths": valid_file_paths,
            "per_file_indicators": per_file_indicators,
            "snippets": snippets,
            "snippets_by_purpose": snippets_by_purpose,
            "sections": sections,
            "subagents": self._sections.subagents,
            "capability_output": capability_output,
            "consulting": consulting,
            "needs": uniq_needs,
            "needs_structured": needs_structured,
            "needs_followup": needs_followup,
            "followup_question": consulting.get("followup_question") if isinstance(consulting, dict) else None,
            "financials": financials,
            "financials_extracted": extracted_financials,
            "financials_series": financials_series,
            "period_changes": period_changes,
            "report": {
                "title": "CFO 财务分析报告",
                "task_type": task_type or "cfo_chat",
                "intent": intent,
                "query": request.text or "",
                "sections": sections,
                "snippets": snippets,
                "snippets_by_purpose": snippets_by_purpose,
                "needs_structured": needs_structured,
            },
        }
