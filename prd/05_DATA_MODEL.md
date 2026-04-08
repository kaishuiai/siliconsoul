# 数据模型与字段口径

本文件定义“对外/对内一致”的核心数据模型字段口径，避免 CLI/API/前端各自解析造成漂移。

## 1. ExpertRequest

语义：对单个 Expert 的一次分析请求。

建议字段（与代码保持一致）：

- request_id：请求唯一标识（可由上层生成）
- text：输入文本
- task_type：任务类型（用于路由/筛选专家）
- user_id：用户标识
- context：上下文（例如历史对话、持仓、偏好）
- extra_params：扩展参数（例如 top_k、数据源开关等）
- timestamp：请求时间戳

## 2. ExpertResult

语义：单个 Expert 的一次输出结果（成功或失败都必须结构化返回）。

建议字段：

- expert_name：专家名
- result：任意结构化对象（JSON 可序列化）
- confidence：0~1
- metadata：版本、模型、数据源、提示词版本等
- timestamp_start / timestamp_end：执行区间（用于耗时计算）
- error：失败时的错误信息（成功可为空）

## 3. AggregatedResult

语义：对一个请求的最终聚合输出。

建议字段：

- request_id
- final_result：最终结论（结构化对象）
- expert_results：ExpertResult 列表
- consensus_score：一致性评分（0~1）
- aggregated_confidence：整体置信度（0~1）
- recommendations：建议列表（可选）
- warnings：风险提示列表（可选）
- timestamp_start / timestamp_end

## 4. 存储记录（Storage）

建议最小可复盘字段：

- request：原始 ExpertRequest（或其关键字段）
- expert_results：原始专家输出（含 error）
- aggregated：最终聚合输出
- system：运行时环境（版本、配置摘要、数据源）

## 5. 口径约束（强烈建议）

- 所有对外输出必须可 JSON 序列化
- error 必须用字符串表达并可直接展示给用户
- confidence 必须在 0~1 之间，且聚合层必须解释置信度来源（例如一致性 + 专家置信度）
