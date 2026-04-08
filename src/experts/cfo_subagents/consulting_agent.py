from __future__ import annotations

from typing import Any, Dict, Optional

from src.experts.cfo_subagents.types import CFOAgentOutput
from src.llm.client import LLMClient


class CFOConsultingAgent:
    name = "cfo_consulting"

    async def run(
        self,
        *,
        query: str,
        llm: Optional[LLMClient],
        context: Optional[Dict[str, Any]] = None,
    ) -> CFOAgentOutput:
        q = (query or "").strip()
        if not q:
            return CFOAgentOutput(
                capability=self.name,
                answer_markdown="需要你提供具体问题。",
                structured={},
                confidence=0.2,
                needs_followup=True,
                followup_question="你希望从 CFO 视角解决什么问题（例如：现金流、预算、盈利能力、成本结构、融资方案）？",
            )

        ctx = context or {}
        user_content = self._build_user_content(q, ctx)

        if llm and llm.is_available():
            system = (
                "你是企业 CFO 助理，面向中国财务语境回答问题。"
                "你需要：先澄清口径/边界，再给结论与建议，并给出可验证的计算或所需数据清单。"
                "不得编造数据；遇到信息不足要明确列出缺口并给出最小补充问题。"
                "避免提供具体投资买卖建议；如涉及投资建议，只能从风险/信息充分性/方法论角度回答。"
                "输出为 Markdown，结构固定："
                "1) 结论 2) 关键依据 3) 风险与假设 4) 下一步要数据/动作"
            )
            content = await llm.chat(
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user_content}],
                temperature=0.2,
                max_tokens=900,
            )
            return CFOAgentOutput(
                capability=self.name,
                answer_markdown=content.strip(),
                structured={"input": q, "context": ctx},
                confidence=0.75,
            )

        indicators = ctx.get("indicators") if isinstance(ctx, dict) else None
        snippets = ctx.get("snippets") if isinstance(ctx, dict) else None
        indicators_md = self._format_indicators(indicators) if isinstance(indicators, dict) else ""
        snippets_md = self._format_snippets(snippets) if isinstance(snippets, list) else ""

        answer = (
            "1) 结论\n"
            "- 当前未接入可用的 LLM 输出层，我可以先按财务框架给你拆解问题。\n\n"
            "2) 关键依据\n"
            "- 需要明确：业务模式、收入确认、成本结构、现金流驱动、资产负债约束。\n\n"
            "3) 风险与假设\n"
            "- 信息不足导致结论不稳，需要补齐关键口径。\n\n"
            "4) 下一步要数据/动作\n"
            "- 请补充：时间范围、口径（含税/不含税、合并/母公司、权责/收付）、关键数值或报表文件路径。"
        )
        if indicators_md or snippets_md:
            answer += "\n\n5) 已提取的材料（供核对）\n"
            if indicators_md:
                answer += indicators_md + "\n"
            if snippets_md:
                answer += snippets_md
        return CFOAgentOutput(
            capability=self.name,
            answer_markdown=answer,
            structured={"input": q, "context": ctx},
            confidence=0.45,
            needs_followup=True,
            followup_question=self._default_followup_question(q),
        )

    def _default_followup_question(self, query: str) -> str:
        q = (query or "").strip()
        lowered = q.lower()
        segment_keywords = ["子业务", "子产品", "产品线", "业务线", "事业部", "segment", "sku"]
        if any(k in q for k in segment_keywords) or any(k in lowered for k in ["segment", "sku"]):
            return (
                "你要分析的子业务/子产品边界是什么（期间、口径、是否含分摊）？\n"
                "建议最小补充材料：\n"
                "1) 该子业务/产品的收入拆分（量×价、渠道/地区/客户）\n"
                "2) 直接成本与毛利（含单位成本/关键成本项）\n"
                "3) 费用分摊口径（销售/研发/管理，分摊规则）\n"
                "4) 经营现金流/回款/应收与存货周转\n"
                "5) 关键经营指标（用户数、ARPU、转化率、留存等）"
            )
        return "你希望分析的期间与口径是什么（合并/母公司、含税/不含税、权责/收付）？是否有报表或业务材料可供解析？"

    def _build_user_content(self, query: str, ctx: Dict[str, Any]) -> str:
        indicators = ctx.get("indicators")
        snippets = ctx.get("snippets")
        s = query
        indicators_md = self._format_indicators(indicators) if isinstance(indicators, dict) else ""
        snippets_md = self._format_snippets(snippets) if isinstance(snippets, list) else ""
        if indicators_md or snippets_md:
            s += "\n\n可用材料：\n"
            if indicators_md:
                s += indicators_md + "\n"
            if snippets_md:
                s += snippets_md
        return s

    def _format_indicators(self, indicators: Dict[str, Any]) -> str:
        if not indicators:
            return ""
        gm = float(indicators.get("gross_margin", 0) or 0) * 100
        nm = float(indicators.get("net_margin", 0) or 0) * 100
        roe = float(indicators.get("roe", 0) or 0) * 100
        da = float(indicators.get("debt_to_assets", 0) or 0) * 100
        return (
            "指标：\n"
            f"- 毛利率：{gm:.2f}%\n"
            f"- 净利率：{nm:.2f}%\n"
            f"- ROE：{roe:.2f}%\n"
            f"- 资产负债率：{da:.2f}%"
        )

    def _format_snippets(self, snippets: List[Any]) -> str:
        if not snippets:
            return ""
        lines = []
        for i, s in enumerate(snippets[:5], start=1):
            if isinstance(s, dict):
                content = str(s.get("snippet") or "").strip()
            else:
                content = str(s).strip()
            if not content:
                continue
            lines.append(f"- 证据{i}：{content}")
        if not lines:
            return ""
        return "证据摘录：\n" + "\n".join(lines)
