# 验收用例与输入输出示例

本文件将核心需求拆解为可执行的验收用例（偏黑盒），并提供 CLI/API 的输入输出示例口径，便于评审、联调与回归。

## A. CLI 验收

### A1. 单次处理（process）

前置条件：

- 可在本机创建 Python 虚拟环境并安装依赖
- 可运行 CLI 入口（python -m src.cli.main 或 ./siliconsoul）

输入示例：

- text：`分析 600000.SH 最近 60 天走势，给出信号与风险点`
- extra_params（建议）：`{"symbol":"600000.SH","period_days":60,"indicators":["MA","RSI","MACD","Bollinger"]}`

验收点：

- 输出包含：
  - final_result（最终结论）与 expert_results（专家明细）
  - 每个 ExpertResult 至少包含：expert_name、confidence、timestamp_start、timestamp_end、error（可为空）、result（结构化对象）
- 单个专家失败不导致整体崩溃；失败原因可在该专家的 error 字段中看到

### A2. 批量处理（batch）

输入示例：

- requests：
  - `分析 600000.SH 的技术指标与信号`
  - `解释 RSI 指标的意义`
  - `根据以下专家结果做决策：...`

验收点：

- 批量每条请求均有独立的 AggregatedResult
- 系统能输出汇总统计（如处理总数、成功数/失败数、平均耗时）
- 每条结果包含 request_id，且可通过 History 页面/API 回放该 request_id 的详情

### A3. 专家列表（experts/list）

验收点：

- 列出当前注册的专家名称、版本、支持的任务类型
- 与代码中的 Expert.get_supported_tasks() 一致

## B. API 验收（规划 + 适配后）

说明：当前仓库包含路由器组件与路由定义，但未提供完整 HTTP Server 启动与 orchestrator 适配层。本节是“契约验收目标”，落地时以 04_API_SPEC.md 为准。

### B1. /api/health

验收点：

- 200 返回 success=true
- data 中至少包含：version、uptime、request_count、status

### B2. /api/experts

验收点：

- 返回专家列表与 supported_tasks

### B3. /api/process

请求体示例：

```json
{
  "text": "分析 600000.SH",
  "task_type": "stock_analysis",
  "context": {},
  "extra_params": {
    "symbol": "600000.SH",
    "period_days": 60,
    "indicators": ["MA", "RSI", "MACD"]
  }
}
```

返回体验收点：

- data 是 AggregatedResult 的 JSON 形态（字段口径见 05_DATA_MODEL.md）
- expert_results 中每个元素是 ExpertResult 的 JSON 形态

### B4. /api/batch

验收点：

- 对每条 request 返回独立 AggregatedResult
- 其中任何一个 request 的失败不会导致整个 batch 失败（最多局部失败）

## C. 存储验收

### C1. 记录写入

前置条件：

- storage.type 设置为 json 或 sqlite（或默认可用）

验收点：

- 每次请求至少落盘：request、expert_results、aggregated
- 可按时间范围或 request_id 查询到记录

## D. 监控验收

验收点：

- 能读取到：请求总数、成功率、平均耗时、最近窗口指标
- 指标更新在请求处理完成后发生，且不因单专家失败而中断

## E. 可靠性验收（边界条件）

- 空输入：返回结构化错误（不崩溃）
- 超时：超过全局超时后仍能返回聚合结果（包含超时专家 error）
- 外部依赖缺失：
  - 无数据源/无网络：股票分析可降级（或明确 error）
  - 无 LLM key：对话专家返回明确 error 或降级到规则回复（以实现为准）
