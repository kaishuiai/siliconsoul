# 部署与运维

## 1. 运行形态

- 本地：Python 虚拟环境运行 CLI 与测试
- HTTP：aiohttp API Server 提供 /api/* 端点
- 容器：Dockerfile / docker-compose
- 脚本：scripts/deploy.sh 提供 deploy/start/stop/restart 操作入口

## 2. 配置管理

建议策略：

- 配置集中管理（ConfigManager）
- 通过配置文件 + 环境变量覆盖
- 关键配置项（示例）：超时、并发、存储类型与路径、数据源开关、日志级别

注意点：

- docker-compose 与脚本对 config/ 挂载存在约定，需补齐默认配置或提供生成器，避免首次启动失败
- 默认配置文件使用 JSON（config/default.json），便于 ConfigManager 直接解析

## 3. 依赖与环境

- 后端依赖：requirements.txt
- 前端依赖：frontend/package.json

建议：

- 固定 Python 版本（例如 3.11）以减少依赖编译与兼容性问题
- CI 中执行：lint + pytest + coverage

## 4. 监控与日志

- SystemMonitor 提供 health/status/metrics 的指标能力（需与 API/CLI 输出对齐）
- 日志建议统一由 logger 模块输出，并确保不打印敏感信息

## 5. 备份与数据

- sqlite/json 落盘目录需可配置
- 建议提供导出命令：按时间范围导出请求与聚合结果用于复盘
