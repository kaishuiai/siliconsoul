# 术语表

- MOE Orchestrator：多专家编排器，负责并发执行与聚合输出
- Expert：专家模块，提供 analyze(request) 的统一接口
- ExpertRequest：专家请求数据结构
- ExpertResult：单专家输出结果数据结构
- AggregatedResult：聚合输出，包含 final_result 与 expert_results
- Consensus Score：专家结果一致性评分
- Knowledge Cache：知识缓存/知识库（本地规则、文档片段、历史分析等）
- Analysis Cache：历史分析缓存，用于复用与复盘
- Realtime Provider：实时行情订阅器，支持 WS + fallback
- Storage Backend：存储后端（memory/json/sqlite）
- Facade/Adapter：适配层，用于将编排器接口对齐到 API 层契约
