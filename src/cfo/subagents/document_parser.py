from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from src.core.tools.runner import ToolRunner


class CFODocumentParser:
    def __init__(self, tool_runner: ToolRunner) -> None:
        self._tool_runner = tool_runner
        self._doc_cache: Dict[str, Dict[str, Any]] = {}

    async def parse(
        self,
        file_path: Optional[str],
        *,
        file_paths: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        if file_paths:
            return await self._parse_many(file_paths)

        if not file_path:
            return None
        if not os.path.exists(file_path):
            return None

        mtime = 0.0
        try:
            mtime = float(os.path.getmtime(file_path))
        except Exception:
            mtime = 0.0

        cache_key = f"{file_path}:{mtime}"
        cached = self._doc_cache.get(cache_key)
        if cached is not None:
            return cached

        parsed = await self._tool_runner.run("cfo.parse_financial_document", file_path=file_path)
        self._doc_cache = {cache_key: parsed}
        return parsed

    async def _parse_many(self, file_paths: List[str]) -> Optional[Dict[str, Any]]:
        normalized: List[str] = []
        for p in file_paths:
            if not p or not isinstance(p, str):
                continue
            if not os.path.exists(p):
                continue
            normalized.append(p)

        if not normalized:
            return None

        parts: List[str] = []
        merged_tables: List[Any] = []
        table_sources: List[str] = []
        documents: List[Dict[str, Any]] = []

        key_parts: List[str] = []
        for p in normalized:
            mtime = 0.0
            try:
                mtime = float(os.path.getmtime(p))
            except Exception:
                mtime = 0.0
            key_parts.append(f"{p}:{mtime}")
        cache_key = "|".join(key_parts)
        cached = self._doc_cache.get(cache_key)
        if cached is not None:
            return cached

        for p in normalized:
            parsed = await self._tool_runner.run("cfo.parse_financial_document", file_path=p)
            documents.append({"file_path": p, "parsed": parsed})

            text = ""
            if isinstance(parsed, dict):
                text = str(parsed.get("text") or "")
            parts.append(f"[file: {os.path.basename(p)}]\n{text}".strip())

            tables = parsed.get("tables") if isinstance(parsed, dict) else None
            if isinstance(tables, list):
                for t in tables:
                    merged_tables.append(t)
                    table_sources.append(p)

        merged: Dict[str, Any] = {
            "text": "\n\n".join([p for p in parts if p]),
            "tables": merged_tables,
            "file_paths": normalized,
            "documents": documents,
            "table_sources": table_sources,
        }
        self._doc_cache = {cache_key: merged}
        return merged
