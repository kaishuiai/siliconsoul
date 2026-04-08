from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple

from src.core.tools.runner import ToolRunner
from src.experts.cfo_subagents.types import CFOAgentOutput
from src.llm.client import LLMClient


class CFOComputationAgent:
    name = "cfo_finance_computation"

    async def run(
        self,
        *,
        query: str,
        tool_runner: ToolRunner,
        llm: Optional[LLMClient],
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> CFOAgentOutput:
        q = (query or "").strip()
        extra_params = extra_params or {}

        spec = extra_params.get("finance_calc")
        if isinstance(spec, dict):
            return await self._run_spec(tool_runner=tool_runner, spec=spec, query=q)

        spec2 = None
        if llm and llm.is_available():
            spec2 = await self._extract_spec_with_llm(llm=llm, query=q)
        if not spec2:
            spec2 = self._extract_spec_rule_based(q)

        if not spec2:
            return CFOAgentOutput(
                capability=self.name,
                answer_markdown=(
                    "我可以做财务计算，但当前信息不足。\n\n"
                    "请用以下任一方式提供输入：\n"
                    "- extra_params.finance_calc={tool,args}\n"
                    "- 或在文本里给出明确参数（例如：NPV 折现率 8% 现金流 -1000,300,400,500）"
                ),
                structured={"input": q},
                confidence=0.35,
                needs_followup=True,
                followup_question="你要算哪一类（NPV/IRR/CAGR/PV/FV/保本点/还款计划）？参数分别是多少？",
            )

        return await self._run_spec(tool_runner=tool_runner, spec=spec2, query=q)

    async def _run_spec(self, *, tool_runner: ToolRunner, spec: Dict[str, Any], query: str) -> CFOAgentOutput:
        tool = str(spec.get("tool", "")).strip()
        args = spec.get("args") if isinstance(spec.get("args"), dict) else {}
        if not tool:
            return CFOAgentOutput(
                capability=self.name,
                answer_markdown="finance_calc.tool 不能为空。",
                structured={"input": query, "spec": spec},
                confidence=0.2,
                needs_followup=True,
                followup_question="请提供 tool（例如 irr/npv/cagr/pv/fv/amortization/break_even/solve_linear/solve_quadratic）",
            )

        try:
            value = await tool_runner.run(tool, **args)
        except Exception as e:
            return CFOAgentOutput(
                capability=self.name,
                answer_markdown=f"计算失败：{str(e)}",
                structured={"input": query, "spec": spec, "error": str(e)},
                confidence=0.2,
                needs_followup=True,
                followup_question="请确认参数口径（百分比是否已除以 100、现金流是否包含 t0、期数单位等）。",
            )

        markdown = self._format_result_markdown(tool=tool, args=args, value=value)
        return CFOAgentOutput(
            capability=self.name,
            answer_markdown=markdown,
            structured={"input": query, "spec": {"tool": tool, "args": args}, "value": value},
            confidence=0.85,
        )

    async def _extract_spec_with_llm(self, *, llm: LLMClient, query: str) -> Optional[Dict[str, Any]]:
        q = (query or "").strip()
        if not q:
            return None

        system = (
            "你是财务计算参数抽取器。"
            "从用户问题中抽取一个可执行的 finance_calc JSON。"
            "只输出 JSON，不要解释。"
            "格式：{"
            '"tool": "irr|npv|cagr|growth_rate|pv|fv|amortization|break_even|solve_linear|solve_quadratic",'
            '"args": { ... }'
            "}。"
            "约定："
            "- 百分比如 8% 转成 0.08"
            "- NPV/IRR 的 cashflows 是数组，包含 t0"
            "- amortization: principal, annual_rate(如0.045), years, payments_per_year"
            "- break_even: fixed_cost, price, variable_cost"
        )
        try:
            raw = await llm.chat(
                messages=[{"role": "system", "content": system}, {"role": "user", "content": q}],
                temperature=0.0,
                max_tokens=350,
            )
            obj = json.loads(raw.strip())
            if not isinstance(obj, dict):
                return None
            if "tool" not in obj or "args" not in obj:
                return None
            if not isinstance(obj.get("args"), dict):
                return None
            return obj
        except Exception:
            return None

    def _extract_spec_rule_based(self, query: str) -> Optional[Dict[str, Any]]:
        q = (query or "").strip()
        if not q:
            return None

        q_lower = q.lower()
        if "irr" in q_lower or "内部收益率" in q or "ir r" in q_lower:
            cfs = self._extract_number_list(q)
            if len(cfs) >= 2:
                return {"tool": "finance.irr", "args": {"cashflows": cfs}}
            return None

        if "npv" in q_lower or "净现值" in q:
            rate = self._extract_first_rate(q)
            cfs = self._extract_number_list(q)
            if rate is not None and len(cfs) >= 2:
                return {"tool": "finance.npv", "args": {"rate": rate, "cashflows": cfs}}
            return None

        if "cagr" in q_lower or "复合增长" in q:
            nums = self._extract_number_list(q)
            if len(nums) >= 3:
                return {"tool": "finance.cagr", "args": {"begin": nums[0], "end": nums[1], "periods": nums[2]}}
            return None

        if "增长率" in q or "同比" in q or "环比" in q:
            nums = self._extract_number_list(q)
            if len(nums) >= 2:
                return {"tool": "finance.growth_rate", "args": {"old": nums[0], "new": nums[1]}}
            return None

        if "现值" in q or "pv" in q_lower:
            rate = self._extract_first_rate(q)
            nums = self._extract_number_list(q)
            if rate is not None and len(nums) >= 1:
                nper = int(round(nums[0]))
                pmt = nums[1] if len(nums) >= 2 else 0.0
                fv = nums[2] if len(nums) >= 3 else 0.0
                return {"tool": "finance.pv", "args": {"rate": rate, "nper": nper, "pmt": pmt, "fv": fv, "when": "end"}}
            return None

        if "终值" in q or "fv" in q_lower:
            rate = self._extract_first_rate(q)
            nums = self._extract_number_list(q)
            if rate is not None and len(nums) >= 1:
                nper = int(round(nums[0]))
                pmt = nums[1] if len(nums) >= 2 else 0.0
                pv = nums[2] if len(nums) >= 3 else 0.0
                return {"tool": "finance.fv", "args": {"rate": rate, "nper": nper, "pmt": pmt, "pv": pv, "when": "end"}}
            return None

        if "保本" in q or "盈亏平衡" in q:
            nums = self._extract_number_list(q)
            if len(nums) >= 3:
                return {
                    "tool": "finance.break_even",
                    "args": {"fixed_cost": nums[0], "price": nums[1], "variable_cost": nums[2]},
                }
            return None

        if "还款" in q or "摊还" in q or "等额" in q:
            rate = self._extract_first_rate(q)
            nums = self._extract_number_list(q)
            if rate is not None and len(nums) >= 2:
                principal = nums[0]
                years = nums[1]
                ppy = int(round(nums[2])) if len(nums) >= 3 else 12
                return {"tool": "finance.amortization", "args": {"principal": principal, "annual_rate": rate, "years": years, "payments_per_year": ppy}}
            return None

        if "解方程" in q or "solve" in q_lower:
            nums = self._extract_number_list(q)
            if len(nums) == 2:
                return {"tool": "math.solve_linear", "args": {"a": nums[0], "b": nums[1]}}
            if len(nums) >= 3:
                return {"tool": "math.solve_quadratic", "args": {"a": nums[0], "b": nums[1], "c": nums[2]}}
            return None

        return None

    def _extract_first_rate(self, text: str) -> Optional[float]:
        m = re.search(r"(-?\d+(?:\.\d+)?)\s*%?", text)
        if not m:
            return None
        raw = m.group(0).strip()
        val = float(m.group(1))
        if "%" in raw:
            return val / 100.0
        if val > 1.5:
            return val / 100.0
        return val

    def _extract_number_list(self, text: str) -> List[float]:
        nums = re.findall(r"-?\d+(?:\.\d+)?", text)
        out: List[float] = []
        for n in nums:
            try:
                out.append(float(n))
            except Exception:
                continue
        return out

    def _format_result_markdown(self, *, tool: str, args: Dict[str, Any], value: Any) -> str:
        head = "## CFO 财务计算结果\n\n"
        arg_lines = "\n".join([f"- {k}: {v}" for k, v in args.items()])
        if isinstance(value, float):
            val_line = f"- result: {value:.10g}"
        else:
            val_line = f"- result: {value}"
        return f"{head}### 输入\n{arg_lines}\n\n### 输出\n{val_line}\n"
