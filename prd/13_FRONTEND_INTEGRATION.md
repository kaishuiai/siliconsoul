# 前端联通与联调清单

## 1. 目标

- 让 frontend/ 在本地开发环境可直接调用后端 /api/* 端点
- 提供最小联调链路：股票历史数据 + 股票分析 + 知识检索

## 2. 前端配置

- 环境变量：REACT_APP_API_URL
  - 建议值：http://localhost:8000/api
  - 示例文件：frontend/.env.example

## 3. 已对齐的后端端点

- GET /api/stocks/<symbol>/history?days=60
- POST /api/analysis/analyze
- GET /api/knowledge/search?q=...

## 4. 前端页面联通

- Dashboard
  - 自动加载：
    - /api/health、/api/experts、/api/monitor/metrics
    - /api/stocks/popular 与部分股票的 /api/stocks/<symbol>/history
- StockAnalysis
  - 点击“开始分析”：
    - 拉取 history 用于图表
    - 调用 analyze 获取信号/指标/支撑阻力/趋势
- KnowledgeBase
  - 点击“智能搜索”：
    - 展示 KnowledgeExpert 的知识条目
- Portfolio
  - 页面加载/保存持仓：
    - /api/portfolio/<user_id>、/api/portfolio/<user_id>/stats
    - /api/portfolio/<user_id>/positions

## 5. 联调检查（curl）

```bash
curl -s http://localhost:8000/api/health

curl -s http://localhost:8000/api/me
```

```bash
curl -s "http://localhost:8000/api/stocks/600000.SH/history?days=30" | head
```

```bash
curl -s -X POST http://localhost:8000/api/analysis/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol":"600000.SH","period_days":60,"indicators":["MA","RSI","MACD"]}'
```

```bash
curl -s "http://localhost:8000/api/knowledge/search?q=RSI"

curl -s "http://localhost:8000/api/history/demo_user?limit=10"
```
