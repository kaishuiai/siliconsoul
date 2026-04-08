from __future__ import annotations

import os
import re
import json
import zipfile
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple


def parse_financial_document(file_path: str) -> Dict[str, Any]:
    ext = os.path.splitext(file_path)[1].lower()
    result: Dict[str, Any] = {"text": "", "tables": []}

    if ext == ".pdf":
        try:
            import fitz

            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            result["text"] = text
        except Exception:
            result["text"] = result.get("text", "")

        try:
            import tabula

            dfs = tabula.read_pdf(file_path, pages="all", multiple_tables=True)
            for df in dfs:
                result["tables"].append(df.to_dict(orient="records"))
        except Exception:
            result["tables"] = result.get("tables", [])

        return result

    if ext in [".xlsx", ".xls"]:
        try:
            import pandas as pd

            xls = pd.ExcelFile(file_path)
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                result["tables"].append({"sheet": sheet_name, "data": df.to_dict(orient="records")})
            try:
                parts: List[str] = []
                for t in result["tables"]:
                    if not isinstance(t, dict):
                        continue
                    sheet = str(t.get("sheet") or "")
                    data = t.get("data")
                    if not isinstance(data, list) or not data:
                        continue
                    preview = data[:20]
                    parts.append(f"[sheet: {sheet}]\n" + json.dumps(preview, ensure_ascii=False))
                result["text"] = "\n\n".join(parts)
            except Exception:
                result["text"] = result.get("text", "")
        except Exception:
            result["tables"] = result.get("tables", [])
        return result

    if ext == ".docx":
        try:
            result["text"] = _extract_docx_text(file_path)
        except Exception:
            result["text"] = result.get("text", "")
        return result

    if ext == ".pptx":
        try:
            result["text"] = _extract_pptx_text(file_path)
        except Exception:
            result["text"] = result.get("text", "")
        return result

    if ext in [".doc", ".ppt"]:
        result["warning"] = f"Unsupported legacy Office format: {ext}. Please convert to .docx/.pptx for parsing."
        return result

    return result


def _extract_docx_text(file_path: str) -> str:
    texts: List[str] = []
    with zipfile.ZipFile(file_path, "r") as zf:
        try:
            xml_bytes = zf.read("word/document.xml")
        except KeyError:
            return ""
        root = ET.fromstring(xml_bytes)
        for node in root.iter():
            if node.tag.endswith("}t") and node.text:
                texts.append(node.text)
    return "\n".join([t for t in texts if t.strip()])


def _extract_pptx_text(file_path: str) -> str:
    parts: List[str] = []
    with zipfile.ZipFile(file_path, "r") as zf:
        slide_paths = [p for p in zf.namelist() if p.startswith("ppt/slides/slide") and p.endswith(".xml")]
        slide_paths.sort()
        for sp in slide_paths:
            xml_bytes = zf.read(sp)
            root = ET.fromstring(xml_bytes)
            slide_texts: List[str] = []
            for node in root.iter():
                if node.tag.endswith("}t") and node.text:
                    slide_texts.append(node.text)
            txt = "\n".join([t for t in slide_texts if t.strip()])
            if txt.strip():
                parts.append(f"[slide: {os.path.basename(sp)}]\n{txt}".strip())
    return "\n\n".join(parts)


def compute_financial_indicators(
    parsed_data: Optional[Dict[str, Any]] = None,
    *,
    financials: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    extracted = extract_financials(parsed_data, financials=financials)
    values = extracted.get("values") if isinstance(extracted, dict) else None
    values = values if isinstance(values, dict) else {}
    is_mock_data = bool(extracted.get("is_mock_data")) if isinstance(extracted, dict) else False
    unit_multiplier = float(extracted.get("unit_multiplier") or 1.0) if isinstance(extracted, dict) else 1.0

    revenue = float(values.get("revenue") or 0.0) * unit_multiplier
    cost = float(values.get("cost") or 0.0) * unit_multiplier
    net_income = float(values.get("net_income") or 0.0) * unit_multiplier
    total_assets = float(values.get("total_assets") or 0.0) * unit_multiplier
    total_equity = float(values.get("total_equity") or 0.0) * unit_multiplier
    total_liabilities = float(values.get("total_liabilities") or 0.0) * unit_multiplier
    inventory = float(values.get("inventory") or 0.0) * unit_multiplier

    gross_margin = (revenue - cost) / revenue if revenue else 0
    net_margin = net_income / revenue if revenue else 0
    roe = net_income / total_equity if total_equity else 0
    debt_to_assets = total_liabilities / total_assets if total_assets else 0
    inventory_turnover = cost / inventory if inventory else 0

    validations: Dict[str, Any] = {}
    if total_assets and total_liabilities and total_equity:
        diff = abs(total_assets - (total_liabilities + total_equity))
        validations["balance_sheet_identity"] = {
            "assets": total_assets,
            "liabilities_plus_equity": total_liabilities + total_equity,
            "diff": diff,
            "diff_ratio": diff / total_assets if total_assets else None,
        }

    return {
        "gross_margin": round(gross_margin, 4),
        "net_margin": round(net_margin, 4),
        "roe": round(roe, 4),
        "debt_to_assets": round(debt_to_assets, 4),
        "inventory_turnover": round(inventory_turnover, 4),
        "is_mock_data": is_mock_data,
        "values": {
            "revenue": revenue,
            "cost": cost,
            "net_income": net_income,
            "total_assets": total_assets,
            "total_equity": total_equity,
            "total_liabilities": total_liabilities,
            "inventory": inventory,
            "operating_cash_flow": float(values.get("operating_cash_flow") or 0.0) * unit_multiplier,
        },
        "validations": validations,
        "unit": extracted.get("unit"),
        "unit_multiplier": unit_multiplier,
        "evidence": extracted.get("evidence"),
    }


def retrieve_document_snippets(
    *,
    query: str,
    document_text: str,
    max_snippets: int = 5,
    max_chars_per_snippet: int = 280,
) -> List[Dict[str, Any]]:
    q = (query or "").strip()
    text = document_text or ""
    if not q or not text:
        return []

    tokens = _extract_query_tokens(q)
    if not tokens:
        return []

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]
    if not paragraphs:
        paragraphs = [line.strip() for line in text.splitlines() if line.strip()]

    scored: List[Dict[str, Any]] = []
    for idx, p in enumerate(paragraphs):
        lower = p.lower()
        score = 0.0
        for t in tokens:
            if t.lower() in lower:
                score += 1.0
        if score <= 0:
            continue
        snippet = p[:max_chars_per_snippet]
        scored.append(
            {
                "evidence_id": f"snip_{idx}",
                "snippet": snippet,
                "score": score,
                "source": "document",
                "location": {"paragraph_index": idx},
            }
        )

    scored.sort(key=lambda x: (x["score"], len(x["snippet"])), reverse=True)
    return scored[: max(0, int(max_snippets))]


def _extract_query_tokens(query: str) -> List[str]:
    parts = re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]{2,}", query)
    tokens: List[str] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if len(p) < 2:
            continue
        tokens.append(p)
    expanded: List[str] = []
    seen = set()
    for t in tokens:
        if t in seen:
            continue
        seen.add(t)
        expanded.append(t)
        if re.fullmatch(r"[\u4e00-\u9fff]{4,}", t):
            for i in range(0, len(t) - 1):
                sub = t[i : i + 2]
                if len(sub) >= 2 and sub not in seen:
                    seen.add(sub)
                    expanded.append(sub)
    return expanded


def _extract_financial_values(
    parsed_data: Optional[Dict[str, Any]],
    financials: Optional[Dict[str, Any]],
) -> Tuple[Dict[str, float], bool, Dict[str, Any], float, Optional[str]]:
    values: Dict[str, float] = {}
    evidence: Dict[str, Any] = {}
    if isinstance(financials, dict):
        unit_multiplier, unit = _infer_unit_multiplier_from_financials(financials)
        for k, v in financials.items():
            try:
                key = str(k)
                if key in ["unit", "unit_multiplier", "evidence"]:
                    continue
                values[key] = float(v)
            except Exception:
                continue
        return values, (not bool(values)), evidence, unit_multiplier, unit

    synonyms = {
        "revenue": ["revenue", "营业收入", "营收", "主营业务收入", "总收入"],
        "cost": ["cost", "营业成本", "主营业务成本", "成本"],
        "net_income": ["net income", "net_income", "净利润", "归母净利润", "净利"],
        "total_assets": ["total assets", "total_assets", "总资产", "资产总计"],
        "total_liabilities": ["total liabilities", "total_liabilities", "总负债", "负债合计"],
        "total_equity": ["total equity", "total_equity", "股东权益", "所有者权益", "净资产", "权益合计"],
        "inventory": ["inventory", "存货"],
        "operating_cash_flow": ["operating cash flow", "operating_cash_flow", "经营活动产生的现金流量净额", "经营现金流", "经营性现金流"],
        "selling_expense": ["selling expense", "selling_expense", "销售费用"],
        "admin_expense": ["admin expense", "admin_expense", "管理费用"],
        "rd_expense": ["rd expense", "rd_expense", "研发费用"],
        "finance_expense": ["finance expense", "finance_expense", "财务费用"],
        "tax_expense": ["tax expense", "tax_expense", "所得税费用", "所得税", "税费"],
    }

    rows: List[Any] = []
    if parsed_data:
        tables = parsed_data.get("tables") or []
        for t in tables:
            if isinstance(t, dict) and "data" in t:
                data = t.get("data") or []
                if isinstance(data, list):
                    rows.extend(data)
            elif isinstance(t, list):
                rows.extend(t)
            else:
                rows.append(t)

    if rows:
        unit_multiplier, unit = _infer_unit_multiplier_from_parsed(parsed_data, rows)
        for metric, keys in synonyms.items():
            if metric in values:
                continue
            hit, ev = _extract_metric_from_rows(rows, keys)
            if hit is not None:
                values[metric] = hit
                if ev:
                    evidence[metric] = ev
    else:
        unit_multiplier, unit = _infer_unit_multiplier_from_parsed(parsed_data, [])

    is_mock_data = False
    if not values:
        is_mock_data = True
        unit_multiplier, unit = 1.0, None
        values = {
            "revenue": 10000.0,
            "cost": 6000.0,
            "net_income": 1500.0,
            "total_assets": 50000.0,
            "total_equity": 20000.0,
            "total_liabilities": 30000.0,
            "inventory": 5000.0,
        }
    return values, is_mock_data, evidence, unit_multiplier, unit


def _extract_metric_from_rows(rows: List[Any], keys: List[str]) -> Tuple[Optional[float], Dict[str, Any]]:
    for idx, row in enumerate(rows):
        try:
            blob = json.dumps(row, ensure_ascii=False)
        except Exception:
            blob = str(row)
        if not blob:
            continue
        if not any(k in blob for k in keys):
            continue
        nums = _extract_numbers(blob)
        if not nums:
            continue
        best = nums[-1]
        if abs(best) < 1e-9:
            best = max(nums, key=lambda x: abs(x))
        return float(best), {"row_index": idx, "matched_keys": keys[:3], "row": row}
    return None, {}


def extract_financials(
    parsed_data: Optional[Dict[str, Any]] = None,
    *,
    financials: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    values, is_mock_data, evidence, unit_multiplier, unit = _extract_financial_values(parsed_data, financials)
    return {
        "values": values,
        "is_mock_data": is_mock_data,
        "evidence": evidence,
        "unit_multiplier": unit_multiplier,
        "unit": unit,
    }


def _infer_unit_multiplier_from_parsed(parsed_data: Optional[Dict[str, Any]], rows: List[Any]) -> Tuple[float, Optional[str]]:
    candidates: List[str] = []
    if parsed_data and parsed_data.get("text"):
        candidates.append(str(parsed_data.get("text") or ""))
    for r in rows[:30]:
        try:
            candidates.append(json.dumps(r, ensure_ascii=False))
        except Exception:
            candidates.append(str(r))
    blob = "\n".join(candidates)
    m = re.search(r"单位[:：]\s*(人民币)?\s*(千元|万元|亿元|元)", blob)
    if not m:
        m = re.search(r"(千元|万元|亿元)\b", blob)
    if not m:
        return 1.0, None
    unit = str(m.group(m.lastindex or 1))
    return _unit_to_multiplier(unit), unit


def _infer_unit_multiplier_from_financials(financials: Dict[str, Any]) -> Tuple[float, Optional[str]]:
    unit = financials.get("unit")
    if isinstance(unit, str) and unit.strip():
        u = unit.strip()
        return _unit_to_multiplier(u), u
    mul = financials.get("unit_multiplier")
    try:
        f = float(mul)
        if f > 0:
            return f, None
    except Exception:
        pass
    return 1.0, None


def _unit_to_multiplier(unit: str) -> float:
    u = (unit or "").strip()
    if u == "元":
        return 1.0
    if u == "千元":
        return 1000.0
    if u == "万元":
        return 10000.0
    if u == "亿元":
        return 100000000.0
    return 1.0


def _extract_numbers(text: str) -> List[float]:
    if not text:
        return []
    t = text
    negs: List[float] = []
    for m in re.findall(r"\(\s*([-+]?\d[\d,]*\.?\d*)\s*\)", t):
        s = m.replace(",", "")
        try:
            negs.append(-float(s))
        except Exception:
            continue
    nums: List[float] = []
    for m in re.findall(r"[-+]?\d[\d,]*\.?\d*", t):
        s = m.replace(",", "")
        try:
            nums.append(float(s))
        except Exception:
            continue
    return negs + nums


def extract_financials_series(
    parsed_data: Optional[Dict[str, Any]] = None,
    *,
    financials: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if isinstance(financials, dict) and financials:
        unit_multiplier, unit = _infer_unit_multiplier_from_financials(financials)
        values: Dict[str, float] = {}
        for k, v in financials.items():
            key = str(k)
            if key in ["unit", "unit_multiplier", "evidence"]:
                continue
            try:
                values[key] = float(v)
            except Exception:
                continue
        item = {
            "source": "provided",
            "file_path": None,
            "period": str(financials.get("period") or ""),
            "period_sort": _period_sort_key(str(financials.get("period") or "")),
            "unit": unit,
            "unit_multiplier": unit_multiplier,
            "values": values,
            "evidence": financials.get("evidence") if isinstance(financials.get("evidence"), dict) else {},
        }
        return {"series": [item], "selected": item}

    docs = parsed_data.get("documents") if isinstance(parsed_data, dict) else None
    if isinstance(docs, list) and docs:
        series: List[Dict[str, Any]] = []
        for d in docs:
            if not isinstance(d, dict):
                continue
            fp = d.get("file_path")
            pd = d.get("parsed")
            if not isinstance(pd, dict):
                continue
            extracted = extract_financials(pd)
            period = _infer_period_label(pd.get("text") if isinstance(pd.get("text"), str) else "", fp if isinstance(fp, str) else None)
            item = {
                "source": "document",
                "file_path": fp if isinstance(fp, str) else None,
                "period": period,
                "period_sort": _period_sort_key(period),
                "unit": extracted.get("unit"),
                "unit_multiplier": extracted.get("unit_multiplier"),
                "values": extracted.get("values"),
                "evidence": extracted.get("evidence"),
                "is_mock_data": extracted.get("is_mock_data"),
            }
            series.append(item)
        series = _sort_series(series)
        selected = series[0] if series else None
        return {"series": series, "selected": selected}

    if parsed_data:
        extracted = extract_financials(parsed_data)
        period = _infer_period_label(str(parsed_data.get("text") or ""), None)
        item = {
            "source": "document",
            "file_path": None,
            "period": period,
            "period_sort": _period_sort_key(period),
            "unit": extracted.get("unit"),
            "unit_multiplier": extracted.get("unit_multiplier"),
            "values": extracted.get("values"),
            "evidence": extracted.get("evidence"),
            "is_mock_data": extracted.get("is_mock_data"),
        }
        return {"series": [item], "selected": item}

    return {"series": [], "selected": None}


def compute_period_changes(
    series: List[Dict[str, Any]],
    *,
    keys: Optional[List[str]] = None,
) -> Dict[str, Any]:
    keys = keys if isinstance(keys, list) and keys else [
        "revenue",
        "cost",
        "net_income",
        "operating_cash_flow",
        "gross_margin",
        "net_margin",
        "opex_ratio",
        "tax_ratio",
        "asset_turnover",
        "equity_multiplier",
        "roe",
        "debt_to_assets",
    ]
    items = _sort_series([s for s in series if isinstance(s, dict)])
    if len(items) < 2:
        return {"latest": None, "previous": None, "changes": {}}

    latest = items[0]
    previous = items[1]
    changes: Dict[str, Any] = {}
    ratio_keys = {"gross_margin", "net_margin", "roe", "debt_to_assets"}
    for k in keys:
        cur = _compute_series_metric(latest, k)
        prev = _compute_series_metric(previous, k)
        if prev is None or abs(prev) < 1e-12 or cur is None:
            continue
        delta = cur - prev
        payload: Dict[str, Any] = {"current": cur, "previous": prev, "delta": delta, "change_rate": delta / prev}
        if str(k) in ratio_keys:
            payload["delta_pp"] = delta * 100
        changes[k] = payload

    return {
        "latest": {"period": latest.get("period"), "file_path": latest.get("file_path")},
        "previous": {"period": previous.get("period"), "file_path": previous.get("file_path")},
        "changes": changes,
    }


def _compute_series_metric(item: Dict[str, Any], key: str) -> Optional[float]:
    k = str(key or "").strip()
    values = item.get("values") if isinstance(item.get("values"), dict) else {}

    if k in {"revenue", "cost", "net_income", "total_assets", "total_liabilities", "total_equity", "inventory", "operating_cash_flow"}:
        return _safe_float(values.get(k))

    revenue = _safe_float(values.get("revenue"))
    cost = _safe_float(values.get("cost"))
    net_income = _safe_float(values.get("net_income"))
    total_assets = _safe_float(values.get("total_assets"))
    total_liabilities = _safe_float(values.get("total_liabilities"))
    total_equity = _safe_float(values.get("total_equity"))

    if k == "gross_margin":
        if revenue is None or cost is None or abs(revenue) < 1e-12:
            return None
        return (revenue - cost) / revenue
    if k == "net_margin":
        if revenue is None or net_income is None or abs(revenue) < 1e-12:
            return None
        return net_income / revenue
    if k == "opex_ratio":
        if revenue is None or abs(revenue) < 1e-12:
            return None
        se = _safe_float(values.get("selling_expense")) or 0.0
        ae = _safe_float(values.get("admin_expense")) or 0.0
        re_ = _safe_float(values.get("rd_expense")) or 0.0
        fe = _safe_float(values.get("finance_expense")) or 0.0
        total = se + ae + re_ + fe
        if abs(total) < 1e-12:
            return None
        return total / revenue
    if k == "tax_ratio":
        if revenue is None or abs(revenue) < 1e-12:
            return None
        te_ = _safe_float(values.get("tax_expense"))
        if te_ is None or abs(te_) < 1e-12:
            return None
        return te_ / revenue
    if k == "roe":
        if net_income is None or total_equity is None or abs(total_equity) < 1e-12:
            return None
        return net_income / total_equity
    if k == "debt_to_assets":
        if total_liabilities is None or total_assets is None or abs(total_assets) < 1e-12:
            return None
        return total_liabilities / total_assets
    if k == "asset_turnover":
        if revenue is None or total_assets is None or abs(total_assets) < 1e-12:
            return None
        return revenue / total_assets
    if k == "equity_multiplier":
        if total_assets is None or total_equity is None or abs(total_equity) < 1e-12:
            return None
        return total_assets / total_equity

    return _safe_float(values.get(k))


def _sort_series(series: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def _key(item: Dict[str, Any]) -> Tuple[int, int, int]:
        ps = item.get("period_sort")
        if isinstance(ps, list) and len(ps) >= 3:
            try:
                return int(ps[0]), int(ps[1]), int(ps[2])
            except Exception:
                return (0, 0, 0)
        return (0, 0, 0)

    with_key = [s for s in series if _key(s) != (0, 0, 0)]
    without_key = [s for s in series if _key(s) == (0, 0, 0)]
    with_key.sort(key=_key, reverse=True)
    return with_key + without_key


def _period_sort_key(period: str) -> List[int]:
    p = (period or "").strip()
    if not p:
        return [0, 0, 0]
    m = re.search(r"(20\d{2})", p)
    year = int(m.group(1)) if m else 0
    q = 0
    m2 = re.search(r"\bQ([1-4])\b", p, flags=re.IGNORECASE)
    if m2:
        q = int(m2.group(1))
    else:
        m3 = re.search(r"第([一二三四1-4])季度", p)
        if m3:
            q = _chinese_quarter_to_int(m3.group(1))
    return [year, q, 0]


def _infer_period_label(text: str, file_path: Optional[str]) -> str:
    t = (text or "")[:2000]
    fp = str(file_path or "")
    for s in [t, fp]:
        p = _infer_period_from_str(s)
        if p:
            return p
    return ""


def _infer_period_from_str(s: str) -> str:
    if not s:
        return ""
    m = re.search(r"(20\d{2})\s*年\s*(第?[一二三四1-4])\s*季度", s)
    if m:
        y = m.group(1)
        q = _chinese_quarter_to_int(m.group(2).replace("第", ""))
        return f"{y}Q{q}"
    m = re.search(r"(20\d{2})\s*Q([1-4])", s, flags=re.IGNORECASE)
    if m:
        return f"{m.group(1)}Q{int(m.group(2))}"
    m = re.search(r"(20\d{2})\s*年\s*度", s)
    if m:
        return f"{m.group(1)}FY"
    m = re.search(r"(20\d{2})", s)
    if m:
        return f"{m.group(1)}FY"
    return ""


def _chinese_quarter_to_int(token: str) -> int:
    t = (token or "").strip()
    if t in ["1", "一"]:
        return 1
    if t in ["2", "二"]:
        return 2
    if t in ["3", "三"]:
        return 3
    if t in ["4", "四"]:
        return 4
    return 0


def _safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _deep_get(obj: Any, path: List[str]) -> Any:
    cur = obj
    for p in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
    return cur
