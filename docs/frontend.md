# SiliconSoul Frontend

## Overview

本目录（frontend/）为 React 前端，用于展示股票分析与知识检索结果。

另提供一个 Streamlit CFO 页面（用于上传财务/业务材料并对话分析）：docs/cfo.md。

## 配置

前端通过环境变量配置后端 API 地址：

- REACT_APP_API_URL：默认值为 http://localhost:8000/api
- REACT_APP_CFO_URL：默认值为 http://localhost:8501（主站导航/首页会新开窗口打开 CFO 上传分析页）

示例文件：

- frontend/.env.example

## 启动

先启动后端 HTTP API：

```bash
python -m src.api_server.server
```

再启动前端：

```bash
cd frontend
npm install
npm start
```

## 已联通的页面

- Dashboard：自动调用：
  - GET /api/health
  - GET /api/experts
  - GET /api/monitor/metrics
  - GET /api/stocks/popular
  - GET /api/stocks/<symbol>
  - GET /api/stocks/<symbol>/history?days=2
- StockAnalysis：点击“开始分析”会调用：
  - GET /api/stocks/<symbol>/history?days=...
  - POST /api/analysis/analyze
- KnowledgeBase：点击“智能搜索”会调用：
  - GET /api/knowledge/search?q=...
- Portfolio：页面加载与更新会调用：
  - GET /api/portfolio/<user_id>
  - GET /api/portfolio/<user_id>/stats
  - POST /api/portfolio/<user_id>/positions
- History：页面加载与查询会调用：
  - GET /api/me
  - GET /api/history/<user_id>
  - GET /api/history/<user_id>/<request_id>

## 鉴权（可选）

- 在 Header 中可填写 API Token（Bearer Token）
- 当后端开启 auth.enabled=true 时，未提供 token 的请求会返回 401
