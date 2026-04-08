# SiliconSoul / PRD 文档索引

本目录用于集中存放与产品设计、业务规划、架构设计、接口契约、运维与发布相关的文档。

## 阅读顺序（推荐）

1. 01_PRD.md：产品目标、用户故事、功能范围、MVP 与验收标准
2. 02_BUSINESS_PLAN.md：业务定位、价值主张、用户与场景、增长与商业化假设
3. 03_ARCHITECTURE.md：系统架构、模块边界、数据流、关键设计决策与约束
4. 04_API_SPEC.md：对外接口契约（当前实现与规划差异一并标注）
5. 05_DATA_MODEL.md：核心数据模型与字段口径
6. 06_OPERATIONS_DEPLOY.md：部署、配置、运维、监控与发布流程
7. 07_ROADMAP.md：里程碑与迭代规划
8. 08_GAPS_AND_RISKS.md：实现/文档对齐问题、测试状态、技术风险与优先级
9. 09_GLOSSARY.md：术语表与统一口径
10. 10_ACCEPTANCE.md：可执行验收用例与输入输出示例
11. 11_E2E_FLOWS.md：端到端链路与字段流转表
12. 12_EXPERT_CATALOG.md：专家目录与逐个专家规格
13. 13_FRONTEND_INTEGRATION.md：前端联通与联调清单
14. 14_PORTFOLIO_SPEC.md：投资组合数据口径与验收
15. 15_AUTH_SPEC.md：鉴权与用户体系（Token）
16. 16_HISTORY_SPEC.md：请求历史与复盘

## 原始资料归档（镜像）

为避免遗漏，已将仓库内现有的文档、脚本与部分配置文件镜像归档到：

- prd/_source/root：根目录下的各类说明/计划/发布资料
- prd/_source/docs：docs/ 下的文档
- prd/_source/scripts：scripts/ 下的运维脚本
- prd/_source/frontend：前端依赖清单（package.json）

后续如需“以 PRD 为唯一真相”，建议以本目录的 01~09 文档为准，并将变更同步回代码与配置。
