from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.core.tools.runner import ToolRunner


class CFOSnippetRetriever:
    def __init__(self, tool_runner: ToolRunner) -> None:
        self._tool_runner = tool_runner

    async def retrieve(
        self,
        *,
        query: str,
        parsed_data: Optional[Dict[str, Any]],
        file_tags_by_path: Optional[Dict[str, Any]] = None,
        max_snippets: int,
        max_chars_per_snippet: int,
    ) -> List[Dict[str, Any]]:
        if not parsed_data:
            return []
        docs = parsed_data.get("documents") if isinstance(parsed_data, dict) else None
        if isinstance(docs, list) and docs:
            all_snips: List[Dict[str, Any]] = []
            for d in docs:
                if not isinstance(d, dict):
                    continue
                fp = d.get("file_path")
                pd = d.get("parsed")
                if not isinstance(fp, str) or not fp.strip():
                    continue
                text = ""
                if isinstance(pd, dict):
                    text = str(pd.get("text") or "")
                if not text.strip():
                    continue
                snips = await self._tool_runner.run(
                    "cfo.retrieve_document_snippets",
                    query=query,
                    document_text=text,
                    max_snippets=max_snippets,
                    max_chars_per_snippet=max_chars_per_snippet,
                )
                purpose = None
                if isinstance(file_tags_by_path, dict):
                    tag = file_tags_by_path.get(fp)
                    if isinstance(tag, dict):
                        purpose = tag.get("purpose")
                    elif isinstance(tag, str):
                        purpose = tag
                if purpose:
                    for s in snips:
                        if isinstance(s, dict):
                            s["purpose"] = purpose
                            s["file_path"] = fp
                            base = float(s.get("score") or 0.0)
                            q = (query or "")
                            bonus = 0.0
                            if isinstance(purpose, str):
                                if purpose in ["成本明细", "费用分摊"] and ("成本" in q or "费用" in q or "毛利" in q):
                                    bonus = 0.6
                                if purpose in ["分部/产品收入"] and ("收入" in q or "价格" in q or "渠道" in q):
                                    bonus = 0.6
                                if purpose in ["经营指标"] and ("留存" in q or "转化" in q or "ARPU" in q or "用户" in q):
                                    bonus = 0.6
                            s["score"] = base + bonus
                all_snips.extend([s for s in snips if isinstance(s, dict)])
            all_snips.sort(key=lambda x: (float(x.get("score") or 0.0), len(str(x.get("snippet") or ""))), reverse=True)
            return all_snips[: max(0, int(max_snippets))]

        text = str(parsed_data.get("text") or "")
        if not text.strip():
            return []
        return await self._tool_runner.run(
            "cfo.retrieve_document_snippets",
            query=query,
            document_text=text,
            max_snippets=max_snippets,
            max_chars_per_snippet=max_chars_per_snippet,
        )
