from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from src.experts.cfo_subagents.simple_retrieval import chunk_text, rank_chunks_by_keyword_overlap
from src.experts.cfo_subagents.types import CFOAgentOutput
from src.experts.knowledge_expert import KnowledgeExpert
from src.llm.client import LLMClient
from src.models.request_response import ExpertRequest


class CFOKnowledgeQAAgent:
    name = "cfo_finance_knowledge_qa"

    def __init__(self) -> None:
        self._knowledge_expert = KnowledgeExpert()

    async def run(
        self,
        *,
        query: str,
        parsed_data: Optional[Dict[str, Any]],
        llm: Optional[LLMClient],
        user_id: str,
    ) -> CFOAgentOutput:
        q = (query or "").strip()
        chunks: List[Dict[str, Any]] = []
        if parsed_data and parsed_data.get("text"):
            raw_chunks = chunk_text(str(parsed_data.get("text") or ""), max_chars=900, overlap=120)
            ranked = rank_chunks_by_keyword_overlap(q, raw_chunks, top_k=5)
            chunks = [{"chunk_id": c.chunk_id, "content": c.content, "score": c.score} for c in ranked]

        external_items = await self._retrieve_general_knowledge(query=q, user_id=user_id)

        if llm and llm.is_available():
            answer = await self._answer_with_llm(llm=llm, query=q, chunks=chunks, external_items=external_items)
            if answer:
                return CFOAgentOutput(
                    capability=self.name,
                    answer_markdown=answer,
                    structured={"input": q, "evidence_chunks": chunks, "knowledge_items": external_items},
                    confidence=0.76,
                )

        md = "## CFO 资料检索问答\n\n"
        md += "### 结论\n"
        md += "- 当前未接入可用的检索增强生成模型，我先返回可用证据片段与相关知识点，便于你快速定位。\n\n"
        if chunks:
            md += "### 报表证据片段\n"
            for c in chunks:
                md += f"- [chunk {c['chunk_id']}]（score={c['score']:.2f}）{str(c['content'])[:240].strip()}\n"
            md += "\n"
        if external_items:
            md += "### 相关知识点\n"
            for it in external_items[:5]:
                md += f"- {it.get('title') or it.get('source')}: {str(it.get('content',''))[:200]}\n"
            md += "\n"
        md += "### 下一步\n- 如果你希望我给出最终回答，请启用 LLM 或指定要引用的 chunk。\n"
        return CFOAgentOutput(
            capability=self.name,
            answer_markdown=md.strip() + "\n",
            structured={"input": q, "evidence_chunks": chunks, "knowledge_items": external_items},
            confidence=0.55,
            needs_followup=True,
            followup_question="你希望我基于报表回答哪个具体问题？（例如：某项费用为何上升、某指标口径解释、政策条款影响）",
        )

    async def _retrieve_general_knowledge(self, *, query: str, user_id: str) -> List[Dict[str, Any]]:
        try:
            req = ExpertRequest(text=query, user_id=user_id, task_type="knowledge_query", extra_params={"top_k": 5})
            res = await self._knowledge_expert.analyze(req)
            items = res.result.get("knowledge_items") if isinstance(res.result, dict) else None
            if isinstance(items, list):
                return [i for i in items if isinstance(i, dict)]
            return []
        except Exception:
            return []

    async def _answer_with_llm(
        self,
        *,
        llm: LLMClient,
        query: str,
        chunks: List[Dict[str, Any]],
        external_items: List[Dict[str, Any]],
    ) -> Optional[str]:
        system = (
            "你是 CFO 资料检索问答助手。"
            "你只能基于提供的证据片段与知识点回答，禁止编造。"
            "回答必须包含引用：对报表证据用 [chunk:<id>]，对知识点用 [kb:<index>]。"
            "输出 Markdown，结构：1) 结论 2) 依据与引用 3) 风险/不确定性 4) 下一步要补充的数据。"
        )
        ev = json.dumps({"chunks": chunks, "knowledge_items": external_items}, ensure_ascii=False)[:8000]
        user = f"问题：{query}\n\n证据：{ev}"
        try:
            content = await llm.chat(
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                temperature=0.2,
                max_tokens=900,
            )
            return content.strip()
        except Exception:
            return None
