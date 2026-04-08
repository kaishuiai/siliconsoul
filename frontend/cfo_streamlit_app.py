import json
import os
from typing import Any, Dict

import requests
import streamlit as st

st.set_page_config(page_title="SiliconSoul - CFO 智能财务分析", layout="wide", page_icon="📈")
st.title("📈 CFO 智能财务分析系统")
st.markdown("基于多智能体协作的财务报表解析、指标计算与专业分析助手")

api_url = os.getenv("CFO_API_URL", "http://localhost:8000/api").rstrip("/")

st.sidebar.header("🔐 访问控制")
token = st.sidebar.text_input("API Token（可选/必填取决于后端配置）", type="password")
headers: Dict[str, str] = {}
if token:
    headers["Authorization"] = f"Bearer {token}"

def _get_me() -> Dict[str, Any]:
    try:
        resp = requests.get(f"{api_url}/me", headers=headers if headers else None, timeout=10)
        payload = resp.json()
        if isinstance(payload, dict) and payload.get("status") == "success":
            return payload.get("data") or {}
    except Exception:
        return {}
    return {}

me = _get_me()
auth_enabled = bool(me.get("auth_enabled", False))
user_id = str(me.get("user_id") or "anonymous")
if auth_enabled and not token:
    st.sidebar.error("后端已开启鉴权：需要输入 Token 才能使用 CFO 页面")
    st.stop()
if auth_enabled and user_id == "anonymous":
    st.sidebar.error("Token 无效或未映射 user_id")
    st.stop()
if auth_enabled:
    st.sidebar.success(f"user_id: {user_id}")

def _preset_dir() -> str:
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "cfo_presets"))
    os.makedirs(base, exist_ok=True)
    return base

def _preset_path(uid: str) -> str:
    safe = "".join([c for c in (uid or "anonymous") if c.isalnum() or c in ("_", "-", ".")]) or "anonymous"
    return os.path.join(_preset_dir(), f"{safe}.json")

def _load_presets(uid: str) -> Dict[str, Any]:
    path = _preset_path(uid)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def _save_presets(uid: str, presets: Dict[str, Any]) -> None:
    path = _preset_path(uid)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(presets, f, ensure_ascii=False, indent=2)

if "cfo_presets" not in st.session_state:
    st.session_state.cfo_presets = _load_presets(user_id)

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

def _current_template_state() -> Dict[str, Any]:
    return {
        "biz_name": st.session_state.get("biz_name", ""),
        "period": st.session_state.get("period", ""),
        "scope": st.session_state.get("scope", ""),
        "include_allocations": bool(st.session_state.get("include_allocations", True)),
        "revenue_breakdown": st.session_state.get("revenue_breakdown", ""),
        "cost_structure": st.session_state.get("cost_structure", ""),
        "allocation_rules": st.session_state.get("allocation_rules", ""),
        "cashflow_working_capital": st.session_state.get("cashflow_working_capital", ""),
        "kpis": st.session_state.get("kpis", ""),
        "questions": st.session_state.get("questions", ""),
    }

def _apply_template_state(state: Dict[str, Any]) -> None:
    st.session_state.biz_name = str(state.get("biz_name") or "")
    st.session_state.period = str(state.get("period") or "")
    st.session_state.scope = str(state.get("scope") or "")
    st.session_state.include_allocations = bool(state.get("include_allocations", True))
    st.session_state.revenue_breakdown = str(state.get("revenue_breakdown") or "")
    st.session_state.cost_structure = str(state.get("cost_structure") or "")
    st.session_state.allocation_rules = str(state.get("allocation_rules") or "")
    st.session_state.cashflow_working_capital = str(state.get("cashflow_working_capital") or "")
    st.session_state.kpis = str(state.get("kpis") or "")
    st.session_state.questions = str(state.get("questions") or "")

def _build_prompt_from_template(state: Dict[str, Any]) -> str:
    lines = []
    name = str(state.get("biz_name") or "").strip()
    if name:
        lines.append(f"请以 CFO 视角对「{name}」做子业务/子产品的单独经营与财务分析。")
    else:
        lines.append("请以 CFO 视角做子业务/子产品的单独经营与财务分析。")
    period = str(state.get("period") or "").strip()
    scope = str(state.get("scope") or "").strip()
    include_allocations = bool(state.get("include_allocations", True))
    if period:
        lines.append(f"- 分析期间：{period}")
    if scope:
        lines.append(f"- 口径/范围：{scope}")
    lines.append(f"- 是否包含费用分摊：{'是' if include_allocations else '否（仅直接口径）'}")

    rb = str(state.get("revenue_breakdown") or "").strip()
    cs = str(state.get("cost_structure") or "").strip()
    ar = str(state.get("allocation_rules") or "").strip()
    cf = str(state.get("cashflow_working_capital") or "").strip()
    kpis = str(state.get("kpis") or "").strip()
    qs = str(state.get("questions") or "").strip()

    if rb:
        lines.append("\n收入拆分（量×价/渠道/地区/客户）：\n" + rb)
    if cs:
        lines.append("\n成本结构与毛利（直接成本/单位成本/关键成本项）：\n" + cs)
    if ar:
        lines.append("\n费用分摊规则（销售/研发/管理）：\n" + ar)
    if cf:
        lines.append("\n现金流与营运资本（回款/应收/存货/预付）：\n" + cf)
    if kpis:
        lines.append("\n关键经营指标（用户数/ARPU/转化率/留存等）：\n" + kpis)
    if qs:
        lines.append("\n我关心的具体问题：\n" + qs)

    lines.append(
        "\n请输出：\n"
        "1) 结论（是否值得继续投入/需要立刻止损的信号）\n"
        "2) P&L 结构与驱动（收入/成本/费用/利润，关键驱动拆解）\n"
        "3) 单位经济模型（如适用：单位毛利、获客/履约成本等）\n"
        "4) 现金流与营运资本风险\n"
        "5) 风险与假设\n"
        "6) 若材料不足，请给出最小补充清单（按优先级）"
    )
    return "\n".join(lines).strip()

def _upload_files(files) -> None:
    if not files:
        return
    multipart = []
    for f in files:
        multipart.append(("file", (f.name, f.getvalue(), f.type)))
    resp = requests.post(f"{api_url}/uploads", files=multipart, headers=headers if headers else None, timeout=60)
    payload = resp.json()
    if not isinstance(payload, dict) or payload.get("status") != "success":
        raise ValueError(payload.get("message") if isinstance(payload, dict) else "upload failed")
    data = payload.get("data") or {}
    out_files = data.get("files") or []
    if not isinstance(out_files, list):
        out_files = []
    for it in out_files:
        if not isinstance(it, dict):
            continue
        file_id = it.get("file_id")
        name = it.get("original_name")
        if not file_id or not name:
            continue
        st.session_state.uploaded_files.append({"file_id": file_id, "original_name": name, "purpose": "财报"})

with st.expander("🧾 子业务/子产品分析模板", expanded=False):
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.text_input("子业务/子产品名称（可选）", key="biz_name")
        st.text_input("分析期间（例如：2024Q1-2025Q2，或 2023-2025）", key="period")
        st.text_input("口径/范围（合并/母公司，含税/不含税，权责/收付，单位）", key="scope")
    with col_b:
        st.checkbox("包含费用分摊", value=True, key="include_allocations")

    st.text_area("收入拆分（量×价/渠道/地区/客户）", height=100, key="revenue_breakdown")
    st.text_area("成本结构与毛利（直接成本/单位成本/关键成本项）", height=100, key="cost_structure")
    st.text_area("费用分摊规则（销售/研发/管理）", height=80, key="allocation_rules")
    st.text_area("现金流与营运资本（回款/应收/存货/预付）", height=80, key="cashflow_working_capital")
    st.text_area("关键经营指标（用户数/ARPU/转化率/留存等）", height=80, key="kpis")
    st.text_area("我关心的具体问题（可选）", height=80, key="questions")

    preset_name = st.text_input("Preset 名称", key="preset_name")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("生成分析指令"):
            st.session_state.generated_prompt = _build_prompt_from_template(_current_template_state())
    with col2:
        if st.button("保存Preset"):
            name = (preset_name or "").strip()
            if name:
                st.session_state.cfo_presets[name] = _current_template_state()
                _save_presets(user_id, st.session_state.cfo_presets)
                st.success("已保存")
    with col3:
        selected_preset = st.selectbox("加载Preset", options=[""] + sorted(list(st.session_state.cfo_presets.keys())), key="selected_preset")
        if st.button("应用Preset"):
            if selected_preset:
                _apply_template_state(st.session_state.cfo_presets.get(selected_preset, {}))
                st.success("已应用")
    with col4:
        if st.button("删除Preset"):
            if selected_preset and selected_preset in st.session_state.cfo_presets:
                st.session_state.cfo_presets.pop(selected_preset, None)
                _save_presets(user_id, st.session_state.cfo_presets)
                st.success("已删除")

    st.download_button(
        "导出所有 Presets（JSON）",
        data=json.dumps(st.session_state.cfo_presets, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name=f"cfo_presets_{user_id}.json",
        mime="application/json",
    )
    imported = st.file_uploader("导入 Presets（JSON）", type=["json"])
    if imported is not None:
        try:
            data = json.loads(imported.getvalue().decode("utf-8"))
            if isinstance(data, dict):
                st.session_state.cfo_presets.update(data)
                _save_presets(user_id, st.session_state.cfo_presets)
                st.success("已导入")
        except Exception:
            st.error("导入失败：文件不是合法 JSON")

    generated_prompt = st.session_state.get("generated_prompt", "")
    if generated_prompt:
        st.text_area("生成的分析指令（可编辑后发送）", value=generated_prompt, height=180, key="generated_prompt_editor")
        if st.button("发送指令"):
            st.session_state.pending_prompt = st.session_state.get("generated_prompt_editor", generated_prompt)

st.sidebar.header("📁 材料上传")
selected_files = st.sidebar.file_uploader(
    "上传财务/业务材料（可多选）",
    type=["pdf", "xlsx", "xls", "pptx", "ppt", "docx", "doc"],
    accept_multiple_files=True,
)
if st.sidebar.button("上传到服务器"):
    try:
        _upload_files(selected_files)
        st.sidebar.success("上传完成")
    except Exception as e:
        st.sidebar.error(f"上传失败：{str(e)}")

if st.session_state.uploaded_files:
    st.sidebar.subheader("已上传文件")
    purposes = ["财报", "分部/产品收入", "成本明细", "费用分摊", "经营指标", "合同/定价", "其他"]
    for it in st.session_state.uploaded_files:
        fid = it.get("file_id")
        name = it.get("original_name")
        if not fid or not name:
            continue
        it["purpose"] = st.sidebar.selectbox(
            name,
            options=purposes,
            index=purposes.index(it.get("purpose") or "财报") if (it.get("purpose") or "财报") in purposes else 0,
            key=f"purpose_{fid}",
        )

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "您好，我是您的专属 CFO 助手。请上传材料，或用模板生成子业务分析指令。"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def _process_prompt(prompt: str) -> None:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    file_ids = [it.get("file_id") for it in st.session_state.uploaded_files if isinstance(it, dict) and it.get("file_id")]
    file_tags = {str(it.get("file_id")): {"purpose": it.get("purpose")} for it in st.session_state.uploaded_files if isinstance(it, dict) and it.get("file_id")}

    body = {
        "text": prompt,
        "task_type": "cfo_chat",
        "context": {},
        "extra_params": {
            "file_ids": file_ids,
            "file_tags": file_tags,
            "business_context": _current_template_state(),
        },
        "expert_names": ["CFOExpert"],
    }

    with st.chat_message("assistant"):
        with st.spinner("CFO 正在深度分析中..."):
            try:
                resp = requests.post(f"{api_url}/process", json=body, headers=headers if headers else None, timeout=120)
                payload = resp.json()
                if not isinstance(payload, dict) or payload.get("status") != "success":
                    raise ValueError(payload.get("message") if isinstance(payload, dict) else "request failed")
                data = payload.get("data") or {}
                results = data.get("results") if isinstance(data, dict) else None
                if not isinstance(results, dict):
                    raise ValueError("bad response")

                cfo_result = None
                for r in results.get("expert_results", []) or []:
                    if isinstance(r, dict) and r.get("expert_name") == "CFOExpert":
                        cfo_result = r
                        break

                out = cfo_result.get("result") if isinstance(cfo_result, dict) else None
                if not isinstance(out, dict):
                    out = results.get("final_result") if isinstance(results.get("final_result"), dict) else {}

                request_id = data.get("request_id") if isinstance(data, dict) else None
                analysis_report = str(out.get("analysis_report", "")) if isinstance(out, dict) else ""
                st.markdown(analysis_report or "（无报告输出）")

                report_md_lines = []
                report_md_lines.append(f"# CFO 分析报告")
                if request_id:
                    report_md_lines.append(f"\nrequest_id: {request_id}\n")
                report_md_lines.append(analysis_report or "")

                needs_structured = out.get("needs_structured") if isinstance(out, dict) else None
                needs = out.get("needs") if isinstance(out, dict) else None
                if isinstance(needs_structured, list) and needs_structured:
                    with st.expander("需要补充的材料（优先级）", expanded=True):
                        by_cat: Dict[str, list] = {}
                        for it in needs_structured[:50]:
                            if not isinstance(it, dict):
                                continue
                            cat = str(it.get("category") or "其他")
                            by_cat.setdefault(cat, []).append(it)
                        for cat, items in by_cat.items():
                            st.markdown(f"**{cat}**")
                            items.sort(key=lambda x: str(x.get("priority") or "P2"))
                            for idx, it in enumerate(items[:20], start=1):
                                text = str(it.get("text") or "").strip()
                                if not text:
                                    continue
                                why = it.get("why")
                                example = it.get("example")
                                label = f"{it.get('priority') or ''} {text}".strip()
                                st.checkbox(label, value=False, key=f"need_{cat}_{idx}_{label}")
                                if isinstance(why, str) and why.strip():
                                    st.caption(f"原因：{why.strip()}")
                                if isinstance(example, str) and example.strip():
                                    st.caption(f"示例：{example.strip()}")
                                report_md_lines.append(f"- [ ] {label}")
                                if isinstance(why, str) and why.strip():
                                    report_md_lines.append(f"  - 原因：{why.strip()}")
                                if isinstance(example, str) and example.strip():
                                    report_md_lines.append(f"  - 示例：{example.strip()}")
                elif isinstance(needs, list) and needs:
                    with st.expander("需要补充的材料（优先级）", expanded=True):
                        for i, n in enumerate(needs[:20], start=1):
                            if isinstance(n, str) and n.strip():
                                st.markdown(f"{i}. {n.strip()}")
                                report_md_lines.append(f"- [ ] {n.strip()}")

                snippets_by_purpose = out.get("snippets_by_purpose") if isinstance(out, dict) else None
                if isinstance(snippets_by_purpose, dict) and snippets_by_purpose:
                    with st.expander("文档依据摘录（按用途）", expanded=False):
                        for purpose, rows in snippets_by_purpose.items():
                            if not isinstance(rows, list) or not rows:
                                continue
                            st.markdown(f"**{purpose}**")
                            for i, s in enumerate(rows[:5], start=1):
                                if not isinstance(s, dict):
                                    continue
                                snippet = str(s.get("snippet") or "").strip()
                                fp = str(s.get("file_path") or "").strip()
                                if snippet:
                                    head = f"{i}. {snippet}"
                                    if fp:
                                        head = f"{head}\n\n来源：{os.path.basename(fp)}"
                                    st.markdown(head)

                consulting = out.get("consulting") if isinstance(out, dict) else None
                if consulting and isinstance(consulting, dict):
                    with st.expander("CFO 咨询子代理建议", expanded=False):
                        st.markdown(str(consulting.get("answer_markdown", "")))
                        if consulting.get("needs_followup") and consulting.get("followup_question"):
                            st.info(str(consulting.get("followup_question")))

                st.download_button(
                    "导出报告（Markdown）",
                    data="\n".join([l for l in report_md_lines if isinstance(l, str)]).encode("utf-8"),
                    file_name=f"cfo_report_{request_id or 'report'}.md",
                    mime="text/markdown",
                )

                st.session_state.messages.append({"role": "assistant", "content": analysis_report or "（无报告输出）"})
            except Exception as e:
                st.error(f"系统错误: {str(e)}")

pending = st.session_state.get("pending_prompt")
if pending:
    st.session_state.pending_prompt = None
    _process_prompt(str(pending))

if prompt := st.chat_input("输入问题（例如：请对某子业务做单独财务分析并指出需要补充的材料）"):
    _process_prompt(prompt)
