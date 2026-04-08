# SiliconSoul

多智能体（MOE）决策支持系统，包含：

- Python 后端 API（aiohttp）+ 多专家编排
- React 主站（Dashboard / Portfolio / KnowledgeBase / History）
- Streamlit CFO 页面（多文档上传、子业务/子产品分析、报告导出）

## 快速开始（Docker Compose）

```bash
docker compose up -d siliconsoul siliconsoul-web siliconsoul-cfo
```

- 主站（React）：通常是 http://localhost:3000
- 后端（API）：通常是 http://localhost:8000/api
- CFO 页面（Streamlit）：http://localhost:8501（主站里会有外链入口新开页面）

## 本地开发

### 后端

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest
```

### 前端

```bash
cd frontend
npm install
npm start
```

## 配置与敏感信息

本仓库不会提交任何 token / 私钥 / app id。请通过环境变量或本地配置文件注入。

- 不要提交：`.env*`、`data/`、`logs/`、`*.db`、`*.key`、`*.pem`（已在 .gitignore 中忽略）
- 推送前建议运行：`./scripts/security_check.sh`
- 前端配置样例：`frontend/.env.example`
- 常用环境变量（示例名，值不要写进仓库）：
  - `TUSHARE_TOKEN`：Tushare 数据源 token
  - `SILICONSOUL_API_TOKENS`：后端鉴权 token 映射（用于 `/api/me` 与授权访问）
  - `REACT_APP_API_URL`：主站请求 API 的 base url
  - `REACT_APP_CFO_URL`：主站外链 CFO 页面 url
  - `CFO_API_URL`：CFO 页面请求后端 API 的 base url

## 文档

- [CFO 场景说明](docs/cfo.md)
- [API 说明](docs/api.md)
- [开发说明](docs/development.md)
