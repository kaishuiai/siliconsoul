# Security Policy

本仓库严禁提交任何敏感信息，包括但不限于：

- Token / API Key / App ID / Secret
- 私钥（.pem/.key/.ppk/.keystore）
- `.env*` 文件、`data/` 运行数据、日志文件

## 配置方式

- 使用环境变量注入（例如：TUSHARE_TOKEN、SILICONSOUL_API_TOKENS）
- 或者使用本地配置文件（例如：config.local.yaml / config.local.json），这些文件应保持在本地且被 .gitignore 忽略

## 推送前检查

建议在推送到 GitHub 之前运行：

```bash
./scripts/security_check.sh
```

如发现敏感信息，请先从 Git 历史中移除并旋转相关密钥。
