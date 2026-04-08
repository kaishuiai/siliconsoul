# SiliconSoul

README Languages:

- 简体中文（默认）：README.md
- 简体中文：[README.zh-CN.md](README.zh-CN.md)
- 繁體中文：[README.zh-TW.md](README.zh-TW.md)
- English：[README.en.md](README.en.md)
- Русский：[README.ru.md](README.ru.md)
- Tiếng Việt：[README.vi.md](README.vi.md)
- Français：[README.fr.md](README.fr.md)
- Español：[README.es.md](README.es.md)
- Italiano：[README.it.md](README.it.md)
- 日本語：[README.ja.md](README.ja.md)
- 한국어：[README.ko.md](README.ko.md)
- ᠮᠠᠨᠵᡠ ᡤᡳᠰᡠᠨ（Manchu）：[README.mnc.md](README.mnc.md)
- ᠮᠣᠩᠭᠣᠯ ᠬᠡᠯᠡ（Mongolian, traditional script）：[README.mn.md](README.mn.md)
- العربية：[README.ar.md](README.ar.md)

> 更新状态（2026-04-08）：PRD Phase 0（第二批）已完成 History 详情口径对齐（新增 expert_results/result 兼容字段），继续推进复盘链路一致性。

## 项目用途 / 价值 / 定位 / 差异点

SiliconSoul 是面向创始人、经营管理者、投研与 CFO 的多智能体（MOE）决策支持产品原型：把业务/财务材料（PDF/Excel/PPT/Word）与多专家并行推理结合，输出带证据的结论、结构化缺口清单与可复盘历史。

### 价值

- 多文档输入 → 输出可复用的“结论 + 依据 + 需要补充什么”
- 子业务/子产品口径分析：可标注材料用途、强制口径校验、输出可执行的补充清单
- 可复盘：历史查询、重放（replay）、对比（diff）、导出报告

### 产品定位

- 这是“分析与复盘工具”，不是会计/财务记账系统，也不替代 ERP/BI
- 适用于：尽调、预算评审、经营分析、子业务拆分分析、投研决策辅助

### 差异点

- 多文档批量上传 + 用途标签（财报/分部收入/成本/分摊/经营指标/合同定价等），证据摘录按用途组织
- 材料不足时输出 needs_structured（可勾选 checklist），并按优先级给出补充材料
- 主站 History 支持 CFO 过滤与复盘工作流（重放/对比/下载）
- 强安全约束：不提交任何 token/私钥/app id；推送前可运行安全检查脚本

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
