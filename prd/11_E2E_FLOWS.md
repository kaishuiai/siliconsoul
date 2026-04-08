# 端到端链路与字段流转

## 1. 核心对象

字段口径以 05_DATA_MODEL.md 为准：

- ExpertRequest：输入
- ExpertResult：单专家输出
- AggregatedResult：聚合输出

## 2. 单次请求（CLI）链路

### 2.1 处理流程（抽象）

1. CLI 接收用户输入（text + 可选 extra_params）
2. CLI 构造 ExpertRequest（user_id、task_type 可选）
3. MOE Orchestrator 并行调用 N 个 Expert.execute(request)
4. Expert.execute 包装 analyze，并保证返回 ExpertResult（异常会转换为 error）
5. Orchestrator 聚合 expert_results，计算 overall_confidence 与 consensus_level
6. 返回 AggregatedResult 并打印/序列化输出
7. 可选：写入 StorageManager、更新 SystemMonitor

### 2.2 字段流转表

| 来源 | 字段 | 去向 | 说明 |
| --- | --- | --- | --- |
| 用户输入 | text | ExpertRequest.text | 主输入 |
| CLI/上层 | task_type | ExpertRequest.task_type | 用于选择专家或辅助聚合 |
| CLI/上层 | extra_params | ExpertRequest.extra_params | 传给专家（如 symbol、top_k） |
| Expert | timestamp_start/end | ExpertResult.timestamp_start/end | 用于 duration_ms 计算 |
| Expert | result | ExpertResult.result | 结构化输出 |
| Expert | error | ExpertResult.error | 失败原因字符串 |
| Orchestrator | expert_results | AggregatedResult.expert_results | 原样汇总 |
| Orchestrator | overall_confidence | AggregatedResult.overall_confidence | 由专家置信度均值等产生 |
| Orchestrator | consensus_level | AggregatedResult.consensus_level | 一致性等级 |
| Orchestrator | final_result | AggregatedResult.final_result | 最终结论（结构化） |

## 3. 批量请求（CLI）链路

- 输入：requests[]（每条可有独立 extra_params）
- 处理：对每条 request 独立调用 orchestrator，并可并发
- 输出：AggregatedResult[] + 批量统计

## 4. 专家执行包装（execute）

原则：

- analyze 内允许抛异常，但 execute 必须吞并并返回 ExpertResult(error=...)
- 即使 analyze 返回类型错误，也必须转换为 ExpertResult(error=...)

## 5. API 链路（规划）

### 5.1 Facade 适配

建议引入 OrchestratorFacade：

- 输入：text/task_type/context/extra_params
- 输出：AggregatedResult（完全一致的数据模型）

这样 API 路由层可以做到：

- 不关心专家细节
- 只负责请求校验、调用 facade、序列化输出

## 6. 序列化口径建议

- ExpertResult 与 AggregatedResult 应直接使用 Pydantic model_dump() 输出，避免手写字段映射
- 所有 result/final_result 必须 JSON 可序列化
