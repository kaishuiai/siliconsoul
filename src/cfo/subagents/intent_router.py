from __future__ import annotations


class CFOIntentRouter:
    def route(self, *, text: str, task_type: str) -> str:
        text_lower = (text or "").lower()
        task = task_type or ""
        if task in ["cfo_finance_computation"] or isinstance(task_type, str) and task_type.startswith("cfo_finance_computation"):
            return "finance_computation"
        if task in ["cfo_finance_text_analysis"]:
            return "finance_text_analysis"
        if task in ["cfo_finance_knowledge_qa"]:
            return "finance_knowledge_qa"
        if task in ["cfo_finance_consulting"]:
            return "finance_consulting"
        if any(k in text_lower for k in ["npv", "irr", "cagr", "pv", "fv"]) or any(k in (text or "") for k in ["净现值", "内部收益率", "现值", "终值", "复合增长", "保本", "盈亏平衡", "还款", "摊还"]):
            return "finance_computation"
        if any(k in (text or "") for k in ["解读", "总结", "抽取", "披露", "附注", "年报", "季报", "审计", "财报"]):
            return "finance_text_analysis"
        if any(k in (text or "") for k in ["根据", "引用", "出处", "政策", "研报", "新闻", "资料"]):
            return "finance_knowledge_qa"
        if "指标" in text_lower or "计算" in text_lower or task == "financial_analysis":
            return "indicator_calculation"
        if "趋势" in text_lower or "预测" in text_lower or task == "trend_prediction":
            return "trend_prediction"
        if "风险" in text_lower or "诊断" in text_lower or task == "risk_diagnosis":
            return "risk_diagnosis"
        if task in ["document_parsing"]:
            return "document_parsing"
        return "finance_consulting"
