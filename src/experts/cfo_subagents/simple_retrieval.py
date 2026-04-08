from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class RetrievalChunk:
    chunk_id: str
    content: str
    score: float


def chunk_text(text: str, *, max_chars: int = 900, overlap: int = 120) -> List[str]:
    t = (text or "").strip()
    if not t:
        return []
    if max_chars <= 0:
        return [t]
    chunks: List[str] = []
    start = 0
    while start < len(t):
        end = min(len(t), start + max_chars)
        chunks.append(t[start:end])
        if end >= len(t):
            break
        start = max(0, end - max(0, overlap))
    return chunks


def rank_chunks_by_keyword_overlap(query: str, chunks: List[str], *, top_k: int = 5) -> List[RetrievalChunk]:
    q = (query or "").lower()
    tokens = _tokens(q)
    if not tokens:
        return []
    ranked: List[RetrievalChunk] = []
    for idx, ch in enumerate(chunks):
        c = ch.lower()
        hit = 0
        for tok in tokens:
            if tok in c:
                hit += 1
        score = hit / max(1, len(tokens))
        if score > 0:
            ranked.append(RetrievalChunk(chunk_id=str(idx), content=ch, score=float(score)))
    ranked.sort(key=lambda x: x.score, reverse=True)
    return ranked[: max(0, int(top_k))]


def _tokens(text: str) -> List[str]:
    raw = re.findall(r"[\u4e00-\u9fff]{2,}|[a-zA-Z]{3,}|\d+(?:\.\d+)?%?", text)
    tokens = []
    for r in raw:
        s = r.strip()
        if not s:
            continue
        tokens.append(s.lower())
    uniq: List[str] = []
    seen = set()
    for t in tokens:
        if t in seen:
            continue
        seen.add(t)
        uniq.append(t)
    return uniq
