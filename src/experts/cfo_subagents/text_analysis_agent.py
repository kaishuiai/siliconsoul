from __future__ import annotations

import json
from typing import Any, Dict, Optional

from src.experts.cfo_subagents.types import CFOAgentOutput
from src.llm.client import LLMClient


class CFOTextAnalysisAgent:
    name = "cfo_finance_text_analysis"

    async def run(
        self,
        *,
        query: str,
        parsed_data: Optional[Dict[str, Any]],
        llm: Optional[LLMClient],
    ) -> CFOAgentOutput:
        q = (query or "").strip()
        if not parsed_data or (not parsed_data.get("text") and not parsed_data.get("tables")):
            return CFOAgentOutput(
                capability=self.name,
                answer_markdown="缺少可分析的财务文本/表格。请上传 PDF/Excel 并提供 file_path。",
                structured={"input": q},
                confidence=0.3,
                needs_followup=True,
                followup_question="请提供报表文件路径（extra_params.file_path）或粘贴需要分析的文本。",
            )

        if llm and llm.is_available():
            extracted = await self._extract_with_llm(llm=llm, query=q, parsed_data=parsed_data)
            if extracted:
                return CFOAgentOutput(
                    capability=self.name,
                    answer_markdown=self._format_markdown(extracted),
                    structured={"input": q, "extracted": extracted},
                    confidence=0.78,
                )

        fallback = {
            "executive_summary": "已解析到报表内容，但当前未接入可用的结构化抽取模型；建议先确认报表期别与口径。",
            "key_metrics": [],
            "risks": ["需要进一步从表格中识别科目与期间，才能输出可对账的指标。"],
            "anomalies": [],
            "questions": ["该报表对应的会计准则/口径是什么？是否为合并报表？期间范围？"],
            "actions": ["提供报表期别与关键科目映射（营收、成本、费用、现金流）"],
        }
        return CFOAgentOutput(
            capability=self.name,
            answer_markdown=self._format_markdown(fallback),
            structured={"input": q, "extracted": fallback},
            confidence=0.5,
            needs_followup=True,
            followup_question="该报表的期间与口径是什么？你最关心盈利、现金流还是偿债能力？",
        )

    async def _extract_with_llm(
        self, *, llm: LLMClient, query: str, parsed_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        text = (parsed_data.get("text") or "").strip()
        tables = parsed_data.get("tables") or []
        table_hint = ""
        if tables:
            try:
                table_hint = json.dumps(tables[:2], ensure_ascii=False)[:2000]
            except Exception:
                table_hint = ""

        system = (
            "你是 CFO 级财务报表解读与信息抽取器。"
            "基于给定文本与表格片段，输出结构化 JSON，不要解释。"
            "JSON schema：{"
            '"executive_summary": str,'
            '"key_metrics": [{"name": str, "value": str, "period": str, "note": str}],'
            '"risks": [str],'
            '"anomalies": [str],'
            '"questions": [str],'
            '"actions": [str]'
            "}。"
            "要求：不得编造未出现的数据；若无法确定数值，用 note 说明缺口。"
        )
        user = (
            f"用户问题：{query}\n\n"
            f"报表文本（可能截断）：{text[:8000]}\n\n"
            f"表格片段（可能截断）：{table_hint}"
        )
        try:
            raw = await llm.chat(
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                temperature=0.0,
                max_tokens=900,
            )
            obj = json.loads(raw.strip())
            if not isinstance(obj, dict):
                return None
            return obj
        except Exception:
            return None

    def _format_markdown(self, extracted: Dict[str, Any]) -> str:
        summary = str(extracted.get("executive_summary", "")).strip()
        metrics = extracted.get("key_metrics") if isinstance(extracted.get("key_metrics"), list) else []
        risks = extracted.get("risks") if isinstance(extracted.get("risks"), list) else []
        anomalies = extracted.get("anomalies") if isinstance(extracted.get("anomalies"), list) else []
        questions = extracted.get("questions") if isinstance(extracted.get("questions"), list) else []
        actions = extracted.get("actions") if isinstance(extracted.get("actions"), list) else []

        md = "## CFO 报表解读\n\n"
        if summary:
            md += f"### 摘要\n{summary}\n\n"
        if metrics:
            md += "### 关键指标/要点\n"
            for m in metrics[:12]:
                if not isinstance(m, dict):
                    continue
                name = str(m.get("name", "")).strip()
                value = str(m.get("value", "")).strip()
                period = str(m.get("period", "")).strip()
                note = str(m.get("note", "")).strip()
                line = f"- {name}: {value}"
                if period:
                    line += f"（{period}）"
                if note:
                    line += f"；{note}"
                md += line + "\n"
            md += "\n"
        if risks:
            md += "### 风险\n" + "\n".join([f"- {r}" for r in risks[:12]]) + "\n\n"
        if anomalies:
            md += "### 异常/需核对\n" + "\n".join([f"- {a}" for a in anomalies[:12]]) + "\n\n"
        if questions:
            md += "### 需要补充的问题\n" + "\n".join([f"- {q}" for q in questions[:8]]) + "\n\n"
        if actions:
            md += "### 建议动作\n" + "\n".join([f"- {a}" for a in actions[:8]]) + "\n\n"
        return md.strip() + "\n"
