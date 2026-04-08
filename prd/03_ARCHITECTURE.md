# 架构设计：SiliconSoul

## 1. 总览

系统由“编排层 + 专家层 + 基础设施层（配置/存储/监控/数据源）”组成。核心思想是将复杂任务拆解给多个 Expert 并行执行，再由编排器聚合输出。

## 2. 组件与职责边界

### 2.1 编排层

- MOE Orchestrator：负责注册专家、并发执行、超时控制、聚合结果、统计信息

### 2.2 专家层

- Expert Base：统一接口与执行包装（超时/异常/性能统计）
- Experts：按领域拆分（股票分析、知识检索、对话、决策、反思、执行、ML 等）

### 2.3 基础设施层

- ConfigManager：集中配置管理（文件/环境变量/运行时 set）
- StorageManager：请求与结果落盘（memory/json/sqlite）
- SystemMonitor：窗口指标与健康判断
- RealtimeDataProvider：行情订阅、回调、缓存与 fallback
- Coordinator/NodeManager：分布式执行与节点管理（目前偏“模拟/框架”）

## 3. 核心数据流

### 3.1 单次请求（逻辑流）

1. 输入：ExpertRequest（text、task_type、user_id、context、extra_params）
2. 编排：为每个专家构造 ExpertRequest（同一 request 的不同视角/参数）
3. 并发执行：每个专家返回 ExpertResult（result、confidence、error、耗时）
4. 聚合输出：AggregatedResult（final_result、expert_results、consensus_metrics、推荐与警告）
5. 可选落盘：StorageManager 写入请求与结果；SystemMonitor 更新指标

### 3.2 关键不变量（建议约束）

- 专家输入/输出必须结构化，字段口径统一（避免 CLI/API/前端各自解析）
- 聚合必须容忍单专家失败，并显式展示失败原因（error 字段）
- 配置必须可追踪：同一次请求应可记录“使用了哪些配置值”

## 4. 接口层形态

当前仓库同时包含：

- CLI：作为主要可用入口
- API Gateway（路由器组件）：包含路由与响应封装，但缺少与编排器的适配与 Web Server 启动
- 前端：React 工程，用于展示结果与图表（是否与后端联通取决于 API 服务形态）

建议的演进：

1. 先提供一个可启动的 HTTP 服务（FastAPI/Flask/aiohttp 之一，需与仓库既有依赖对齐）
2. 引入 orchestrator facade，保证 API 所需方法签名与编排器一致

## 5. 实现/设计差异（必须关注）

- API 路由层假设 orchestrator 具备 process()/monitor/config_manager 等接口，但当前编排器主入口为 process_request(ExpertRequest)，需要适配层
- 配置文件路径与 docker-compose/script 的挂载约定需要补齐默认配置或提供生成器

详见 08_GAPS_AND_RISKS.md。
