from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple


class CFOSectionOrchestrator:
    def __init__(self) -> None:
        self._subagents = [
            "executive_summary",
            "key_metrics",
            "multi_file_comparison",
            "driver_decomposition",
            "risk_diagnosis",
            "outlook",
            "forecasting",
            "valuation_overview",
            "peer_comparison",
            "sensitivity_analysis",
            "recommendations",
            "qna",
        ]

    @property
    def subagents(self) -> List[str]:
        return list(self._subagents)

    def plan(self, *, task_type: str, intent: str) -> List[str]:
        task = task_type or ""
        if task == "document_parsing" or intent == "document_parsing":
            return []
        if task == "risk_diagnosis" or intent == "risk_diagnosis":
            return ["risk_diagnosis", "executive_summary", "qna"]
        if task == "trend_prediction" or intent == "trend_prediction":
            return ["outlook", "forecasting", "executive_summary", "qna"]
        if task == "financial_analysis" or intent == "indicator_calculation":
            return [
                "executive_summary",
                "key_metrics",
                "multi_file_comparison",
                "driver_decomposition",
                "risk_diagnosis",
                "outlook",
                "forecasting",
                "valuation_overview",
                "peer_comparison",
                "sensitivity_analysis",
                "recommendations",
                "qna",
            ]
        return ["executive_summary", "key_metrics", "risk_diagnosis", "recommendations", "qna"]

    def build_sections(
        self,
        *,
        query: str,
        task_type: str,
        intent: str,
        indicators: Dict[str, Any],
        snippets: List[Dict[str, Any]],
        has_parsed_data: bool,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        extra_params = extra_params or {}
        selected = self.plan(task_type=task_type, intent=intent)
        sections: Dict[str, Any] = {}

        if "executive_summary" in selected:
            sections["executive_summary"] = self._executive_summary(indicators=indicators, has_parsed_data=has_parsed_data)
        if "key_metrics" in selected:
            sections["key_metrics"] = self._key_metrics(indicators=indicators)
        if "multi_file_comparison" in selected:
            sections["multi_file_comparison"] = self._multi_file_comparison(extra_params=extra_params)
        if "driver_decomposition" in selected:
            sections["driver_decomposition"] = self._driver_decomposition(extra_params=extra_params)
        if "risk_diagnosis" in selected:
            sections["risk_diagnosis"] = self._risk_diagnosis(indicators=indicators)
        if "outlook" in selected:
            sections["outlook"] = self._outlook(indicators=indicators)
        if "forecasting" in selected:
            sections["forecasting"] = self._forecasting(query=query, indicators=indicators, extra_params=extra_params)
        if "valuation_overview" in selected:
            sections["valuation_overview"] = self._valuation_overview(query=query, indicators=indicators, extra_params=extra_params)
        if "peer_comparison" in selected:
            sections["peer_comparison"] = self._peer_comparison(query=query, indicators=indicators, extra_params=extra_params)
        if "sensitivity_analysis" in selected:
            sections["sensitivity_analysis"] = self._sensitivity_analysis(query=query, indicators=indicators, extra_params=extra_params)
        if "recommendations" in selected:
            sections["recommendations"] = self._recommendations(indicators=indicators)
        if "qna" in selected:
            sections["qna"] = self._qna(query=query, snippets=snippets, has_parsed_data=has_parsed_data)

        return sections

    def assemble_report(
        self,
        *,
        query: str,
        intent: str,
        task_type: str,
        indicators: Dict[str, Any],
        sections: Dict[str, Any],
        has_parsed_data: bool,
        snippets_by_purpose: Optional[Dict[str, List[Dict[str, Any]]]] = None,
        business_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        lines: List[str] = []
        lines.append("## CFO 财务分析报告")
        lines.append("")
        lines.append(f"- 任务类型：{task_type or 'cfo_chat'}")
        lines.append(f"- 意图：{intent}")
        lines.append(f"- 触发问题：{query}")
        if indicators.get("is_mock_data"):
            lines.append("- 数据口径：当前关键指标为演示口径，建议上传结构化报表或在 extra_params.financials 提供标准化数据")
        lines.append("")

        section_purpose_map: Dict[str, List[str]] = {
            "executive_summary": ["财报", "分部/产品收入", "成本明细", "费用分摊", "经营指标", "合同/定价", "其他", "未标注"],
            "key_metrics": ["财报", "经营指标", "未标注"],
            "multi_file_comparison": ["财报", "分部/产品收入", "成本明细", "费用分摊", "经营指标", "未标注"],
            "driver_decomposition": ["财报", "分部/产品收入", "成本明细", "费用分摊", "未标注"],
            "risk_diagnosis": ["财报", "成本明细", "费用分摊", "经营指标", "合同/定价", "未标注"],
            "outlook": ["经营指标", "分部/产品收入", "合同/定价", "其他", "未标注"],
            "forecasting": ["经营指标", "分部/产品收入", "财报", "未标注"],
            "valuation_overview": ["合同/定价", "财报", "经营指标", "未标注"],
            "peer_comparison": ["财报", "经营指标", "未标注"],
            "sensitivity_analysis": ["合同/定价", "成本明细", "费用分摊", "未标注"],
            "recommendations": ["财报", "分部/产品收入", "成本明细", "费用分摊", "经营指标", "合同/定价", "其他", "未标注"],
            "qna": ["财报", "分部/产品收入", "成本明细", "费用分摊", "经营指标", "合同/定价", "其他", "未标注"],
        }

        def _basename(p: str) -> str:
            return p.split("/")[-1] if isinstance(p, str) and p else ""

        def _collect_section_sources(section_key: str) -> Dict[str, List[str]]:
            if not isinstance(snippets_by_purpose, dict) or not snippets_by_purpose:
                return {}
            allowed = section_purpose_map.get(section_key)
            out: Dict[str, List[str]] = {}
            for purpose, rows in snippets_by_purpose.items():
                if allowed is not None and purpose not in allowed:
                    continue
                if not isinstance(rows, list) or not rows:
                    continue
                files: List[str] = []
                seen = set()
                for s in rows:
                    if not isinstance(s, dict):
                        continue
                    fp = s.get("file_path")
                    b = _basename(str(fp)) if fp else ""
                    if not b or b in seen:
                        continue
                    seen.add(b)
                    files.append(b)
                    if len(files) >= 3:
                        break
                if files:
                    out[str(purpose)] = files
            return out

        if isinstance(snippets_by_purpose, dict) and snippets_by_purpose:
            lines.append("### 章节引用概览")
            lines.append("")
            for key in [
                "executive_summary",
                "key_metrics",
                "multi_file_comparison",
                "driver_decomposition",
                "risk_diagnosis",
                "outlook",
                "forecasting",
                "valuation_overview",
                "peer_comparison",
                "sensitivity_analysis",
                "recommendations",
                "qna",
            ]:
                if not isinstance(sections.get(key), dict):
                    continue
                srcs = _collect_section_sources(key)
                if not srcs:
                    continue
                parts: List[str] = []
                for purpose in sorted(list(srcs.keys())):
                    files = srcs.get(purpose) or []
                    if files:
                        parts.append(f"{purpose}（{', '.join(files)}）")
                if parts:
                    lines.append(f"- {key}: " + "；".join(parts))
            lines.append("")

        include_allocations = False
        allocation_rules = ""
        if isinstance(business_context, dict):
            include_allocations = bool(business_context.get("include_allocations", False))
            allocation_rules = str(business_context.get("allocation_rules") or "").strip()

        order = [
            "executive_summary",
            "key_metrics",
            "multi_file_comparison",
            "driver_decomposition",
            "risk_diagnosis",
            "outlook",
            "forecasting",
            "valuation_overview",
            "peer_comparison",
            "sensitivity_analysis",
            "recommendations",
            "qna",
        ]
        for key in order:
            sec = sections.get(key)
            if not isinstance(sec, dict):
                continue
            md = str(sec.get("markdown") or "").strip()
            if md:
                lines.append(md)
                lines.append("")
            if include_allocations and not allocation_rules and key in {"driver_decomposition", "risk_diagnosis", "recommendations"}:
                lines.append("> *提示：当前选择“包含费用分摊”，但未提供分摊规则，本节结论可能偏离真实子业务口径。*")
                lines.append("")
            if isinstance(snippets_by_purpose, dict) and snippets_by_purpose:
                srcs = _collect_section_sources(key)
                if srcs:
                    lines.append("#### 本节依据")
                    for purpose in sorted(list(srcs.keys())):
                        files = srcs.get(purpose) or []
                        if files:
                            lines.append(f"- {purpose}：{', '.join(files)}")
                    lines.append("")

        if has_parsed_data:
            lines.append("> *分析包含自动解析结果，复杂附注仍建议人工复核。*")
        else:
            lines.append("> *分析基于问题描述与默认假设，若提供报表文件可进一步提升准确性。*")

        return "\n".join(lines).strip() + "\n"

    def _driver_decomposition(self, *, extra_params: Dict[str, Any]) -> Dict[str, Any]:
        series = extra_params.get("financials_series")
        if not isinstance(series, list) or len(series) < 2:
            return {"title": "驱动拆解", "markdown": "", "evidence_ids": []}

        latest = series[0] if isinstance(series[0], dict) else None
        previous = series[1] if isinstance(series[1], dict) else None
        if not isinstance(latest, dict) or not isinstance(previous, dict):
            return {"title": "驱动拆解", "markdown": "", "evidence_ids": []}

        pv = previous.get("values") if isinstance(previous.get("values"), dict) else {}
        lv = latest.get("values") if isinstance(latest.get("values"), dict) else {}

        prev_label = str(previous.get("period") or "") or "previous"
        latest_label = str(latest.get("period") or "") or "latest"

        r0 = self._safe_float(pv.get("revenue"))
        c0 = self._safe_float(pv.get("cost"))
        ni0 = self._safe_float(pv.get("net_income"))
        r1 = self._safe_float(lv.get("revenue"))
        c1 = self._safe_float(lv.get("cost"))
        ni1 = self._safe_float(lv.get("net_income"))

        lines: List[str] = ["### 驱动拆解（DuPont + 利润率桥）"]
        lines.append(f"- 期间：{prev_label} → {latest_label}")

        def _ratio(n: Optional[float], d: Optional[float]) -> Optional[float]:
            if n is None or d is None or abs(d) < 1e-12:
                return None
            return n / d

        gm0 = _ratio((r0 - c0) if (r0 is not None and c0 is not None) else None, r0)
        gm1 = _ratio((r1 - c1) if (r1 is not None and c1 is not None) else None, r1)
        nm0 = _ratio(ni0, r0)
        nm1 = _ratio(ni1, r1)

        se0 = self._safe_float(pv.get("selling_expense"))
        ae0 = self._safe_float(pv.get("admin_expense"))
        rd0 = self._safe_float(pv.get("rd_expense"))
        fe0 = self._safe_float(pv.get("finance_expense"))
        se1 = self._safe_float(lv.get("selling_expense"))
        ae1 = self._safe_float(lv.get("admin_expense"))
        rd1 = self._safe_float(lv.get("rd_expense"))
        fe1 = self._safe_float(lv.get("finance_expense"))
        opex0 = None if all(v is None for v in [se0, ae0, rd0, fe0]) else (float(se0 or 0.0) + float(ae0 or 0.0) + float(rd0 or 0.0) + float(fe0 or 0.0))
        opex1 = None if all(v is None for v in [se1, ae1, rd1, fe1]) else (float(se1 or 0.0) + float(ae1 or 0.0) + float(rd1 or 0.0) + float(fe1 or 0.0))
        opexr0 = _ratio(opex0, r0) if opex0 is not None else None
        opexr1 = _ratio(opex1, r1) if opex1 is not None else None

        tx0 = self._safe_float(pv.get("tax_expense"))
        tx1 = self._safe_float(lv.get("tax_expense"))
        txr0 = _ratio(tx0, r0) if tx0 is not None else None
        txr1 = _ratio(tx1, r1) if tx1 is not None else None

        lines.append("")
        lines.append("| 指标 | 上期 | 本期 | 变化 |")
        lines.append("| --- | --- | --- | --- |")
        lines.append(f"| 毛利率 | {self._fmt_pct(gm0)} | {self._fmt_pct(gm1)} | {self._pp_delta(gm0, gm1)}pp |")
        lines.append(f"| 净利率 | {self._fmt_pct(nm0)} | {self._fmt_pct(nm1)} | {self._pp_delta(nm0, nm1)}pp |")
        if opexr0 is not None or opexr1 is not None:
            lines.append(f"| 费用率（销管研财） | {self._fmt_pct(opexr0)} | {self._fmt_pct(opexr1)} | {self._pp_delta(opexr0, opexr1)}pp |")
        if txr0 is not None or txr1 is not None:
            lines.append(f"| 税费率 | {self._fmt_pct(txr0)} | {self._fmt_pct(txr1)} | {self._pp_delta(txr0, txr1)}pp |")

        ta0 = self._safe_float(pv.get("total_assets"))
        tl0 = self._safe_float(pv.get("total_liabilities"))
        te0 = self._safe_float(pv.get("total_equity"))
        ta1 = self._safe_float(lv.get("total_assets"))
        tl1 = self._safe_float(lv.get("total_liabilities"))
        te1 = self._safe_float(lv.get("total_equity"))

        at0 = _ratio(r0, ta0)
        at1 = _ratio(r1, ta1)
        em0 = _ratio(ta0, te0)
        em1 = _ratio(ta1, te1)
        roe0 = _ratio(ni0, te0)
        roe1 = _ratio(ni1, te1)
        lev0 = _ratio(tl0, ta0)
        lev1 = _ratio(tl1, ta1)

        if any(v is not None for v in [at0, at1, em0, em1, roe0, roe1]):
            lines.append("")
            lines.append("**DuPont（ROE = 净利率 × 资产周转 × 权益乘数）**")
            lines.append("")
            lines.append("| 指标 | 上期 | 本期 | 变化 |")
            lines.append("| --- | --- | --- | --- |")
            lines.append(f"| 资产周转率 | {self._safe_fmt_float(at0)} | {self._safe_fmt_float(at1)} | {self._safe_delta(at0, at1)} |")
            lines.append(f"| 权益乘数 | {self._safe_fmt_float(em0)} | {self._safe_fmt_float(em1)} | {self._safe_delta(em0, em1)} |")
            lines.append(f"| ROE | {self._fmt_pct(roe0)} | {self._fmt_pct(roe1)} | {self._pp_delta(roe0, roe1)}pp |")
            if lev0 is not None or lev1 is not None:
                lines.append(f"| 资产负债率 | {self._fmt_pct(lev0)} | {self._fmt_pct(lev1)} | {self._pp_delta(lev0, lev1)}pp |")

        pc = extra_params.get("period_changes")
        if isinstance(pc, dict) and isinstance(pc.get("changes"), dict) and pc.get("latest") and pc.get("previous"):
            lines.append("")
            lines.append("**最近两期变化（由模型抽取计算）**")
            for k, v in (pc.get("changes") or {}).items():
                if not isinstance(v, dict):
                    continue
                label = {
                    "revenue": "收入",
                    "cost": "成本",
                    "net_income": "净利润",
                    "operating_cash_flow": "经营现金流",
                    "gross_margin": "毛利率",
                    "net_margin": "净利率",
                    "opex_ratio": "费用率（销管研财）",
                    "tax_ratio": "税费率",
                    "asset_turnover": "资产周转率",
                    "equity_multiplier": "权益乘数",
                    "roe": "ROE",
                    "debt_to_assets": "资产负债率",
                }.get(str(k), str(k))
                if str(k) in {"gross_margin", "net_margin", "roe", "debt_to_assets", "opex_ratio", "tax_ratio"}:
                    try:
                        dpp = float(v.get("delta_pp"))
                    except Exception:
                        continue
                    lines.append(f"- {label}：{dpp:.2f}pp")
                else:
                    try:
                        rate = float(v.get("change_rate"))
                    except Exception:
                        continue
                    lines.append(f"- {label}：{rate * 100:.2f}%")

        md = "\n".join(lines).strip()
        return {"title": "驱动拆解", "markdown": md, "evidence_ids": []}

    def _safe_fmt_float(self, v: Any) -> str:
        f = self._safe_float(v)
        if f is None:
            return "-"
        return f"{f:.4f}"

    def _safe_delta(self, a: Any, b: Any) -> str:
        fa = self._safe_float(a)
        fb = self._safe_float(b)
        if fa is None or fb is None:
            return "-"
        return f"{(fb - fa):.4f}"

    def _multi_file_comparison(self, *, extra_params: Dict[str, Any]) -> Dict[str, Any]:
        items = extra_params.get("per_file_indicators")
        file_paths = extra_params.get("file_paths")
        if not isinstance(items, list) or len(items) < 2:
            series = extra_params.get("financials_series")
            if not isinstance(series, list) or len(series) < 2:
                return {"title": "多文件对比", "markdown": "", "evidence_ids": []}
            rows: List[Dict[str, Any]] = []
            for it in series:
                if not isinstance(it, dict):
                    continue
                period = str(it.get("period") or "").strip() or "-"
                values = it.get("values") if isinstance(it.get("values"), dict) else {}
                rev = self._safe_float(values.get("revenue"))
                cost = self._safe_float(values.get("cost"))
                ni = self._safe_float(values.get("net_income"))
                gm = (rev - cost) / rev if (rev is not None and cost is not None and rev) else None
                nm = ni / rev if (ni is not None and rev) else None
                rows.append(
                    {
                        "period": period,
                        "revenue": rev,
                        "net_income": ni,
                        "gross_margin": gm,
                        "net_margin": nm,
                        "unit": it.get("unit"),
                        "unit_multiplier": it.get("unit_multiplier"),
                        "is_mock_data": bool(it.get("is_mock_data")) if isinstance(it.get("is_mock_data"), bool) else False,
                    }
                )
            rows = [r for r in rows if r.get("revenue") is not None]
            if len(rows) < 2:
                return {"title": "多文件对比", "markdown": "", "evidence_ids": []}

            lines: List[str] = ["### 多文件对比（多期数据）", "", "| 期间 | 毛利率 | 净利率 | 收入 | 净利润 | |", "| --- | --- | --- | --- | --- |"]
            for r in rows:
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            str(r.get("period") or "-"),
                            self._fmt_pct(r.get("gross_margin")),
                            self._fmt_pct(r.get("net_margin")),
                            self._fmt_num(r.get("revenue")),
                            self._fmt_num(r.get("net_income")),
                        ]
                    )
                    + " |"
                )

            values0 = series[0].get("values") if isinstance(series[0], dict) and isinstance(series[0].get("values"), dict) else {}
            has_balance = any(k in values0 for k in ["total_assets", "total_liabilities", "total_equity"])
            if has_balance:
                lines.append("")
                lines.append("| 期间 | 资产负债率 | ROE | 总资产 | 总负债 | 净资产 | |")
                lines.append("| --- | --- | --- | --- | --- | --- |")
                for it in series:
                    if not isinstance(it, dict):
                        continue
                    period = str(it.get("period") or "").strip() or "-"
                    values = it.get("values") if isinstance(it.get("values"), dict) else {}
                    rev = self._safe_float(values.get("revenue"))
                    cost = self._safe_float(values.get("cost"))
                    ni = self._safe_float(values.get("net_income"))
                    ta = self._safe_float(values.get("total_assets"))
                    tl = self._safe_float(values.get("total_liabilities"))
                    te = self._safe_float(values.get("total_equity"))
                    roe = (ni / te) if (ni is not None and te is not None and abs(te) > 1e-12) else None
                    lev = (tl / ta) if (tl is not None and ta is not None and abs(ta) > 1e-12) else None
                    lines.append(
                        "| "
                        + " | ".join(
                            [
                                period,
                                self._fmt_pct(lev),
                                self._fmt_pct(roe),
                                self._fmt_num(ta),
                                self._fmt_num(tl),
                                self._fmt_num(te),
                            ]
                        )
                        + " |"
                    )

            pc = extra_params.get("period_changes")
            if isinstance(pc, dict) and isinstance(pc.get("changes"), dict) and pc.get("latest") and pc.get("previous"):
                latest = pc.get("latest") if isinstance(pc.get("latest"), dict) else {}
                previous = pc.get("previous") if isinstance(pc.get("previous"), dict) else {}
                lines.append("")
                lines.append(f"**最近两期变化**（{str(latest.get('period') or '-') } vs {str(previous.get('period') or '-')}）")
                for k, v in (pc.get("changes") or {}).items():
                    if not isinstance(v, dict):
                        continue
                    label = {
                        "revenue": "收入",
                        "cost": "成本",
                        "net_income": "净利润",
                        "operating_cash_flow": "经营现金流",
                        "gross_margin": "毛利率",
                        "net_margin": "净利率",
                        "roe": "ROE",
                        "debt_to_assets": "资产负债率",
                    }.get(str(k), str(k))
                    if str(k) in {"gross_margin", "net_margin", "roe", "debt_to_assets"}:
                        try:
                            dpp = float(v.get("delta_pp"))
                        except Exception:
                            continue
                        lines.append(f"- {label}变动：{dpp:.2f}pp")
                    else:
                        try:
                            rate = float(v.get("change_rate"))
                        except Exception:
                            continue
                        lines.append(f"- {label}变动：{rate * 100:.2f}%")

            md = "\n".join(lines).strip()
            return {"title": "多文件对比", "markdown": md, "evidence_ids": [], "structured": {"series": rows}}

        rows: List[Dict[str, Any]] = []
        for it in items:
            if not isinstance(it, dict):
                continue
            fp = it.get("file_path")
            ind = it.get("indicators")
            if not isinstance(fp, str) or not fp.strip():
                continue
            ind = ind if isinstance(ind, dict) else {}
            base = fp.strip().split("/")[-1]
            entity, period_label, period_key = self._infer_entity_and_period(base)
            rows.append(
                {
                    "file_path": fp.strip(),
                    "file_name": base,
                    "entity": entity,
                    "period_label": period_label,
                    "period_key": period_key,
                    "indicators": ind,
                }
            )

        if len(rows) < 2:
            return {"title": "多文件对比", "markdown": "", "evidence_ids": []}

        groups: Dict[str, List[Dict[str, Any]]] = {}
        for r in rows:
            k = str(r.get("entity") or "default")
            groups.setdefault(k, []).append(r)

        lines: List[str] = ["### 多文件对比（期间/主体）"]
        if isinstance(file_paths, list) and len(file_paths) > 1:
            lines.append(f"- 文件数：{len(file_paths)}")

        for entity, g in groups.items():
            g_sorted = sorted(g, key=lambda x: (x.get("period_key") is None, x.get("period_key") or (9999, 99, 99), x.get("file_name") or ""))
            if len(groups) > 1:
                lines.append("")
                lines.append(f"#### 主体：{entity}")

            lines.append("")
            lines.append("| 期间 | 文件 | 毛利率 | 净利率 | ROE | 资产负债率 |")
            lines.append("| --- | --- | --- | --- | --- | --- |")
            for r in g_sorted:
                ind = r.get("indicators") if isinstance(r.get("indicators"), dict) else {}
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            str(r.get("period_label") or "-"),
                            str(r.get("file_name") or "-"),
                            self._fmt_pct(ind.get("gross_margin")),
                            self._fmt_pct(ind.get("net_margin")),
                            self._fmt_pct(ind.get("roe")),
                            self._fmt_pct(ind.get("debt_to_assets")),
                        ]
                    )
                    + " |"
                )

            deltas = self._compute_period_deltas(g_sorted)
            if deltas:
                lines.append("")
                lines.append("**关键变化（相邻期间，pp）**")
                for d in deltas[:6]:
                    lines.append(
                        f"- {d['from']} → {d['to']}：毛利率 {d['gm_pp']}pp，净利率 {d['nm_pp']}pp，ROE {d['roe_pp']}pp，资产负债率 {d['lev_pp']}pp"
                    )

            yoy = self._compute_yoy_deltas(g_sorted)
            if yoy:
                lines.append("")
                lines.append("**关键变化（同比，pp）**")
                for d in yoy[:6]:
                    lines.append(
                        f"- {d['from']} → {d['to']}：毛利率 {d['gm_pp']}pp，净利率 {d['nm_pp']}pp，ROE {d['roe_pp']}pp，资产负债率 {d['lev_pp']}pp"
                    )

        md = "\n".join(lines).strip()
        return {"title": "多文件对比", "markdown": md, "evidence_ids": []}

    def _safe_float(self, value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except Exception:
            return None

    def _fmt_num(self, value: Any) -> str:
        v = self._safe_float(value)
        if v is None:
            return "-"
        av = abs(v)
        if av >= 1e8:
            return f"{v / 1e8:.2f}亿"
        if av >= 1e4:
            return f"{v / 1e4:.2f}万"
        return f"{v:.2f}"

    def _compute_period_deltas(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        prev = None
        for r in rows:
            ind = r.get("indicators") if isinstance(r.get("indicators"), dict) else {}
            if prev is None:
                prev = r
                continue
            ind_prev = prev.get("indicators") if isinstance(prev.get("indicators"), dict) else {}
            out.append(
                {
                    "from": str(prev.get("period_label") or prev.get("file_name") or "-"),
                    "to": str(r.get("period_label") or r.get("file_name") or "-"),
                    "gm_pp": self._pp_delta(ind_prev.get("gross_margin"), ind.get("gross_margin")),
                    "nm_pp": self._pp_delta(ind_prev.get("net_margin"), ind.get("net_margin")),
                    "roe_pp": self._pp_delta(ind_prev.get("roe"), ind.get("roe")),
                    "lev_pp": self._pp_delta(ind_prev.get("debt_to_assets"), ind.get("debt_to_assets")),
                }
            )
            prev = r
        return out

    def _compute_yoy_deltas(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        by_key: Dict[Tuple[int, int, int], Dict[str, Any]] = {}
        for r in rows:
            pk = r.get("period_key")
            if isinstance(pk, tuple) and len(pk) == 3:
                try:
                    by_key[(int(pk[0]), int(pk[1]), int(pk[2]))] = r
                except Exception:
                    continue

        out: List[Dict[str, Any]] = []
        for r in rows:
            pk = r.get("period_key")
            if not isinstance(pk, tuple) or len(pk) != 3:
                continue
            try:
                year, kind, idx = int(pk[0]), int(pk[1]), int(pk[2])
            except Exception:
                continue
            if kind not in (1, 2, 3):
                continue
            prev = by_key.get((year - 1, kind, idx))
            if prev is None:
                continue
            ind = r.get("indicators") if isinstance(r.get("indicators"), dict) else {}
            ind_prev = prev.get("indicators") if isinstance(prev.get("indicators"), dict) else {}
            out.append(
                {
                    "from": str(prev.get("period_label") or prev.get("file_name") or "-"),
                    "to": str(r.get("period_label") or r.get("file_name") or "-"),
                    "gm_pp": self._pp_delta(ind_prev.get("gross_margin"), ind.get("gross_margin")),
                    "nm_pp": self._pp_delta(ind_prev.get("net_margin"), ind.get("net_margin")),
                    "roe_pp": self._pp_delta(ind_prev.get("roe"), ind.get("roe")),
                    "lev_pp": self._pp_delta(ind_prev.get("debt_to_assets"), ind.get("debt_to_assets")),
                }
            )
        return out

    def _pp_delta(self, a: Any, b: Any) -> str:
        try:
            fa = float(a)
            fb = float(b)
        except Exception:
            return "-"
        return f"{(fb - fa) * 100:.2f}"

    def _infer_entity_and_period(self, file_name: str) -> Tuple[str, str, Optional[Tuple[int, int, int]]]:
        base = (file_name or "").strip()
        name_no_ext = re.sub(r"\.[A-Za-z0-9]+$", "", base)
        entity = "default"
        for sep in ["_", "-", " "]:
            if sep in name_no_ext:
                first = name_no_ext.split(sep, 1)[0].strip()
                if first and not re.search(r"20\d{2}", first):
                    entity = first
                break

        year = None
        m_year = re.search(r"(20\d{2})", name_no_ext)
        if m_year:
            try:
                year = int(m_year.group(1))
            except Exception:
                year = None

        label = name_no_ext if name_no_ext else base
        if year is None:
            return entity, label, None

        q = re.search(r"(?:Q([1-4])|([1-4])季)", name_no_ext, flags=re.IGNORECASE)
        if q:
            qn = q.group(1) or q.group(2)
            try:
                qi = int(qn)
            except Exception:
                qi = 0
            return entity, f"{year}Q{qi}", (year, 1, qi)

        h = re.search(r"(?:H([12])|(上半年|下半年))", name_no_ext, flags=re.IGNORECASE)
        if h:
            if h.group(1):
                hi = int(h.group(1))
            else:
                hi = 1 if h.group(2) == "上半年" else 2
            return entity, f"{year}H{hi}", (year, 2, hi)

        if re.search(r"(年报|年度|年)", name_no_ext):
            return entity, f"{year}FY", (year, 3, 4)

        return entity, label, (year, 9, 9)

    def _executive_summary(self, *, indicators: Dict[str, Any], has_parsed_data: bool) -> Dict[str, Any]:
        gm = float(indicators.get("gross_margin") or 0.0) * 100
        nm = float(indicators.get("net_margin") or 0.0) * 100
        lev = float(indicators.get("debt_to_assets") or 0.0) * 100
        note = "当前指标来自解析数据" if has_parsed_data and not indicators.get("is_mock_data") else "当前指标为演示口径"
        md = "\n".join(
            [
                "### 执行摘要",
                f"- 盈利能力：毛利率 {gm:.2f}% ，净利率 {nm:.2f}%",
                f"- 杠杆水平：资产负债率 {lev:.2f}%",
                f"- 数据口径：{note}",
            ]
        )
        return {"title": "执行摘要", "markdown": md, "evidence_ids": []}

    def _key_metrics(self, *, indicators: Dict[str, Any]) -> Dict[str, Any]:
        md = "\n".join(
            [
                "### 核心财务指标",
                f"- 毛利率：{float(indicators.get('gross_margin') or 0.0) * 100:.2f}%",
                f"- 净利率：{float(indicators.get('net_margin') or 0.0) * 100:.2f}%",
                f"- ROE：{float(indicators.get('roe') or 0.0) * 100:.2f}%",
                f"- 资产负债率：{float(indicators.get('debt_to_assets') or 0.0) * 100:.2f}%",
                f"- 存货周转率：{float(indicators.get('inventory_turnover') or 0.0):.2f}",
            ]
        )
        return {"title": "核心财务指标", "markdown": md, "evidence_ids": []}

    def _risk_diagnosis(self, *, indicators: Dict[str, Any]) -> Dict[str, Any]:
        lev = float(indicators.get("debt_to_assets") or 0.0)
        nm = float(indicators.get("net_margin") or 0.0)
        risks: List[str] = []
        if lev >= 0.7:
            risks.append("- 偿债与再融资风险：杠杆水平偏高，需关注债务期限结构与利率敏感性。")
        elif lev >= 0.5:
            risks.append("- 杠杆压力：资产负债率中高位，建议评估现金流覆盖与偿债安排。")
        else:
            risks.append("- 杠杆风险：资产负债率处于可控区间，重点关注短期流动性。")

        if nm <= 0.03:
            risks.append("- 盈利波动：净利率偏低，对成本或价格变动更敏感。")
        else:
            risks.append("- 盈利质量：净利率尚可，但需进一步拆解一次性损益与现金含量。")

        bs = indicators.get("validations", {}).get("balance_sheet_identity")
        if isinstance(bs, dict):
            ratio = bs.get("diff_ratio")
            try:
                ratio_f = float(ratio)
            except Exception:
                ratio_f = None
            if ratio_f is not None and ratio_f > 0.02:
                risks.append("- 数据一致性：资产=负债+权益恒等式偏差较大，建议复核报表口径/单位/合并范围。")

        md = "\n".join(["### 风险诊断分析"] + risks)
        return {"title": "风险诊断分析", "markdown": md, "evidence_ids": []}

    def _outlook(self, *, indicators: Dict[str, Any]) -> Dict[str, Any]:
        md = "\n".join(
            [
                "### 趋势预测与展望",
                "- 若能补充多期财务数据（至少 8 个季度或 3 年），可输出更可解释的营收/利润预测与驱动拆解。",
                "- 当前默认输出为口径提示：支持在上传表格后自动抽取多期数据并生成 3 年滚动预测。",
            ]
        )
        return {"title": "趋势预测与展望", "markdown": md, "evidence_ids": []}

    def _forecasting(self, *, query: str, indicators: Dict[str, Any], extra_params: Dict[str, Any]) -> Dict[str, Any]:
        forecast = extra_params.get("forecast") if isinstance(extra_params.get("forecast"), dict) else {}
        years = int(forecast.get("years", 3)) if forecast else 3
        years = max(1, min(10, years))
        values = indicators.get("values") if isinstance(indicators.get("values"), dict) else {}
        revenue = values.get("revenue")
        growth = forecast.get("revenue_growth_rate")
        try:
            growth_f = float(growth) if growth is not None else None
        except Exception:
            growth_f = None

        if revenue is None:
            md = "\n".join(
                [
                    "### 预测与规划（经营与财务）",
                    "- 当前缺少可用的收入/利润基数，无法生成可对账的预测表。",
                    "- 建议提供：extra_params.financials.revenue（当期收入）或上传包含收入科目的 Excel/PDF。",
                ]
            )
            return {"title": "预测与规划", "markdown": md, "evidence_ids": [], "structured": {"needs": ["financials.revenue"]}}

        base = float(revenue)
        if growth_f is None:
            md = "\n".join(
                [
                    "### 预测与规划（经营与财务）",
                    "- 已识别到收入基数，但缺少增长假设。",
                    "- 建议提供：extra_params.forecast.revenue_growth_rate（如 0.08 表示 8%）。",
                ]
            )
            return {
                "title": "预测与规划",
                "markdown": md,
                "evidence_ids": [],
                "structured": {"base_revenue": base, "needs": ["forecast.revenue_growth_rate"]},
            }

        series: List[Dict[str, Any]] = []
        cur = base
        for i in range(1, years + 1):
            cur = cur * (1.0 + growth_f)
            series.append({"year": i, "revenue": round(cur, 2), "growth_rate": growth_f})

        lines = ["### 预测与规划（经营与财务）", "- 收入预测（基于增长假设）："]
        for row in series:
            lines.append(f"- 第 {row['year']} 年：收入 {row['revenue']}")
        md = "\n".join(lines)
        return {
            "title": "预测与规划",
            "markdown": md,
            "evidence_ids": [],
            "structured": {"revenue_forecast": series, "assumptions": {"revenue_growth_rate": growth_f, "base_revenue": base}},
        }

    def _valuation_overview(self, *, query: str, indicators: Dict[str, Any], extra_params: Dict[str, Any]) -> Dict[str, Any]:
        valuation = extra_params.get("valuation") if isinstance(extra_params.get("valuation"), dict) else {}
        years = int(valuation.get("years", 5)) if valuation else 5
        years = max(3, min(15, years))
        values = indicators.get("values") if isinstance(indicators.get("values"), dict) else {}

        fcf0 = valuation.get("fcf0")
        if fcf0 is None:
            fcf0 = values.get("operating_cash_flow")
        if fcf0 is None:
            fcf0 = values.get("net_income")

        try:
            fcf0_f = float(fcf0) if fcf0 is not None else None
        except Exception:
            fcf0_f = None

        discount = valuation.get("discount_rate")
        terminal_g = valuation.get("terminal_growth_rate")
        growth = valuation.get("fcf_growth_rate")
        try:
            discount_f = float(discount) if discount is not None else None
        except Exception:
            discount_f = None
        try:
            terminal_g_f = float(terminal_g) if terminal_g is not None else None
        except Exception:
            terminal_g_f = None
        try:
            growth_f = float(growth) if growth is not None else None
        except Exception:
            growth_f = None

        needs: List[str] = []
        if fcf0_f is None:
            needs.append("valuation.fcf0 或 financials.operating_cash_flow/net_income")
        if discount_f is None:
            needs.append("valuation.discount_rate")
        if terminal_g_f is None:
            needs.append("valuation.terminal_growth_rate")
        if growth_f is None:
            needs.append("valuation.fcf_growth_rate")

        if needs:
            md = "\n".join(
                [
                    "### 估值概览（DCF）",
                    "- 当前缺少足够的估值输入，无法输出可复现的估值结果。",
                    "- 建议提供（示例）：extra_params.valuation={fcf0: 1000, fcf_growth_rate: 0.08, discount_rate: 0.1, terminal_growth_rate: 0.03, years: 5}",
                ]
            )
            return {"title": "估值概览", "markdown": md, "evidence_ids": [], "structured": {"needs": needs}}

        if discount_f <= terminal_g_f:
            md = "\n".join(
                [
                    "### 估值概览（DCF）",
                    "- 折现率必须大于永续增长率，否则永续价值会发散。",
                    "- 请调整 valuation.discount_rate 或 valuation.terminal_growth_rate。",
                ]
            )
            return {
                "title": "估值概览",
                "markdown": md,
                "evidence_ids": [],
                "structured": {"discount_rate": discount_f, "terminal_growth_rate": terminal_g_f},
            }

        cashflows: List[float] = []
        cur = fcf0_f
        for _ in range(years):
            cur = cur * (1.0 + growth_f)
            cashflows.append(cur)

        pv_sum = 0.0
        for t, cf in enumerate(cashflows, start=1):
            pv_sum += cf / ((1.0 + discount_f) ** t)

        terminal_cf = cashflows[-1] * (1.0 + terminal_g_f)
        terminal_value = terminal_cf / (discount_f - terminal_g_f)
        terminal_pv = terminal_value / ((1.0 + discount_f) ** years)
        enterprise_value = pv_sum + terminal_pv

        md = "\n".join(
            [
                "### 估值概览（DCF）",
                f"- 预测期：{years} 年",
                f"- 折现率：{discount_f:.4f}；永续增长率：{terminal_g_f:.4f}；预测期 FCF 增长率：{growth_f:.4f}",
                f"- 预测期现金流现值：{pv_sum:.2f}",
                f"- 永续价值现值：{terminal_pv:.2f}",
                f"- 企业价值（EV）：{enterprise_value:.2f}",
            ]
        )
        return {
            "title": "估值概览",
            "markdown": md,
            "evidence_ids": [],
            "structured": {
                "assumptions": {
                    "fcf0": fcf0_f,
                    "fcf_growth_rate": growth_f,
                    "discount_rate": discount_f,
                    "terminal_growth_rate": terminal_g_f,
                    "years": years,
                },
                "projection": {"cashflows": cashflows},
                "valuation": {
                    "pv_cashflows": pv_sum,
                    "pv_terminal": terminal_pv,
                    "enterprise_value": enterprise_value,
                },
            },
        }

    def _peer_comparison(self, *, query: str, indicators: Dict[str, Any], extra_params: Dict[str, Any]) -> Dict[str, Any]:
        peers = extra_params.get("peers")
        if not isinstance(peers, list) or not peers:
            md = "\n".join(
                [
                    "### 同业对比",
                    "- 当前缺少同业数据，无法输出可对比的表格。",
                    "- 建议提供：extra_params.peers=[{name, gross_margin, net_margin, roe, debt_to_assets}]。",
                ]
            )
            return {"title": "同业对比", "markdown": md, "evidence_ids": [], "structured": {"needs": ["peers"]}}

        base = {
            "name": str(extra_params.get("company_name") or "当前公司"),
            "gross_margin": indicators.get("gross_margin"),
            "net_margin": indicators.get("net_margin"),
            "roe": indicators.get("roe"),
            "debt_to_assets": indicators.get("debt_to_assets"),
        }
        rows: List[Dict[str, Any]] = [base]
        for p in peers[:20]:
            if not isinstance(p, dict):
                continue
            row = {
                "name": str(p.get("name") or p.get("ticker") or "peer"),
                "gross_margin": p.get("gross_margin"),
                "net_margin": p.get("net_margin"),
                "roe": p.get("roe"),
                "debt_to_assets": p.get("debt_to_assets"),
            }
            rows.append(row)

        lines = ["### 同业对比", "| 公司 | 毛利率 | 净利率 | ROE | 资产负债率 |", "| --- | --- | --- | --- | --- |"]
        for r in rows:
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(r.get("name") or ""),
                        self._fmt_pct(r.get("gross_margin")),
                        self._fmt_pct(r.get("net_margin")),
                        self._fmt_pct(r.get("roe")),
                        self._fmt_pct(r.get("debt_to_assets")),
                    ]
                )
                + " |"
            )
        md = "\n".join(lines)
        return {"title": "同业对比", "markdown": md, "evidence_ids": [], "structured": {"rows": rows}}

    def _sensitivity_analysis(self, *, query: str, indicators: Dict[str, Any], extra_params: Dict[str, Any]) -> Dict[str, Any]:
        valuation = extra_params.get("valuation") if isinstance(extra_params.get("valuation"), dict) else {}
        base = self._valuation_overview(query=query, indicators=indicators, extra_params=extra_params)
        structured = base.get("structured") if isinstance(base, dict) else None
        if not isinstance(structured, dict) or "valuation" not in structured:
            md = "\n".join(["### 敏感性分析", "- 当前未生成可复现的估值结果，无法做敏感性分析。"])
            return {"title": "敏感性分析", "markdown": md, "evidence_ids": [], "structured": {"needs": ["valuation inputs"]}}

        assumptions = structured.get("assumptions") if isinstance(structured.get("assumptions"), dict) else {}
        try:
            fcf0 = float(assumptions.get("fcf0"))
            g = float(assumptions.get("fcf_growth_rate"))
            r0 = float(assumptions.get("discount_rate"))
            tg0 = float(assumptions.get("terminal_growth_rate"))
            years = int(assumptions.get("years"))
        except Exception:
            md = "\n".join(["### 敏感性分析", "- 估值参数解析失败，无法做敏感性分析。"])
            return {"title": "敏感性分析", "markdown": md, "evidence_ids": [], "structured": {"error": "bad assumptions"}}

        r_list = [r0 - 0.01, r0, r0 + 0.01]
        tg_list = [tg0 - 0.005, tg0, tg0 + 0.005]
        grid: List[Dict[str, Any]] = []
        for r in r_list:
            for tg in tg_list:
                if r <= tg:
                    grid.append({"discount_rate": r, "terminal_growth_rate": tg, "enterprise_value": None})
                    continue
                ev = self._dcf_ev(fcf0=fcf0, growth=g, discount=r, terminal_growth=tg, years=years)
                grid.append({"discount_rate": r, "terminal_growth_rate": tg, "enterprise_value": round(ev, 2)})

        lines = ["### 敏感性分析（EV）", "- 以折现率与永续增长率为主轴的估值区间："]
        for row in grid:
            ev = row["enterprise_value"]
            ev_s = "N/A" if ev is None else str(ev)
            lines.append(f"- 折现率 {row['discount_rate']:.4f} / 永续增长 {row['terminal_growth_rate']:.4f} => EV {ev_s}")
        md = "\n".join(lines)
        return {"title": "敏感性分析", "markdown": md, "evidence_ids": [], "structured": {"grid": grid}}

    def _dcf_ev(self, *, fcf0: float, growth: float, discount: float, terminal_growth: float, years: int) -> float:
        cashflows: List[float] = []
        cur = fcf0
        for _ in range(years):
            cur = cur * (1.0 + growth)
            cashflows.append(cur)

        pv_sum = 0.0
        for t, cf in enumerate(cashflows, start=1):
            pv_sum += cf / ((1.0 + discount) ** t)

        terminal_cf = cashflows[-1] * (1.0 + terminal_growth)
        terminal_value = terminal_cf / (discount - terminal_growth)
        terminal_pv = terminal_value / ((1.0 + discount) ** years)
        return pv_sum + terminal_pv

    def _fmt_pct(self, v: Any) -> str:
        try:
            f = float(v)
        except Exception:
            return "-"
        return f"{f * 100:.2f}%"

    def _recommendations(self, *, indicators: Dict[str, Any]) -> Dict[str, Any]:
        md = "\n".join(
            [
                "### CFO 行动建议",
                "- 口径与数据治理：统一科目映射与单位（元/万元/亿元），建立报表抓取与校验规则。",
                "- 经营改善：围绕毛利率、费用率、存货周转制定季度经营抓手与责任人。",
                "- 风险管理：补齐现金流滚动预测与债务期限结构表，建立预警阈值。",
            ]
        )
        return {"title": "CFO 行动建议", "markdown": md, "evidence_ids": []}

    def _qna(self, *, query: str, snippets: List[Dict[str, Any]], has_parsed_data: bool) -> Dict[str, Any]:
        if not snippets:
            md = "\n".join(
                [
                    "### 针对问题的答复",
                    "- 当前未检索到与问题直接相关的文档证据片段。",
                    "- 建议上传财报/经营数据表，或在问题中明确科目与期间（如 2023Q4、2024Q1）。",
                ]
            )
            return {"title": "针对问题的答复", "markdown": md, "evidence_ids": []}

        hits = snippets[:3]
        lines = ["### 针对问题的答复", "- 结合已上传材料，优先关注以下证据片段："]
        evidence_ids: List[str] = []
        for s in hits:
            eid = str(s.get("evidence_id") or "")
            snippet = str(s.get("snippet") or "").strip()
            if not snippet:
                continue
            if eid:
                evidence_ids.append(eid)
            lines.append(f"- 证据 {eid or '-'}：{snippet}")
        return {"title": "针对问题的答复", "markdown": "\n".join(lines), "evidence_ids": evidence_ids}
