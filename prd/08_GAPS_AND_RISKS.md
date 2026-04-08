# 现状差异、风险与待办

## 1. 设计/实现对齐差异

- API Gateway 与编排器接口不一致：路由层假设 orchestrator 存在 process()/monitor/config_manager 等接口，但现有编排器主入口为 process_request(ExpertRequest)，需要 Facade/Adapter
- 配置落地缺口：docker-compose 与脚本对 config/ 挂载存在约定，但仓库默认配置文件未内置，首次启动易失败
- 文档提及的部分模块在当前 src/ 中未找到对应实现（更像规划稿与现状存在漂移）

## 2. 工程健康度（测试与依赖）

发现的问题（已处理）：

- requirements.txt 存在不可安装依赖（python-logging）已移除
- requirements.txt 存在依赖冲突（numpy 2.x 与 chromadb 要求不兼容）已调整为 numpy 1.26.4，并将 chromadb 下限提升到 >=0.5.0
- 单测依赖的 cache 模块缺失已补齐（src/cache）

仍需关注：

- 测试覆盖率阈值（pytest.ini fail-under=70）需要以“全量测试通过”为前提评估；局部运行单个测试文件会显示低覆盖率属于正常现象
- 若要稳定在 CI/本机一键通过，需要固定 Python 版本并提供标准化的 venv/依赖安装路径

## 3. 运行期风险

- 多外部数据源（WebSocket/HTTP/第三方数据）不稳定：需要超时、重试、fallback 与熔断策略，并将策略参数化
- 专家输出口径漂移：必须以 05_DATA_MODEL.md 为准，避免出现多套字段（status/data vs expert_name/result）
- 聚合一致性：当前聚合规则需要明确其统计口径与可解释输出（例如一致性分数如何计算）

## 4. 优先级建议

P0（阻断可用性）：

- 统一 ExpertResult/AggregatedResult 输出字段口径，并让 CLI/API/前端共享同一序列化逻辑
- 补齐默认配置与首次启动体验（config 生成/示例）

P1（提升可控性）：

- API 服务形态落地（选择框架 + 适配层 + 健康检查/监控）
- 存储与导出能力增强（用于复盘）

P2（能力扩展）：

- 分布式执行真实化（替换模拟 sleep）
- Expert 插件化与版本/灰度
