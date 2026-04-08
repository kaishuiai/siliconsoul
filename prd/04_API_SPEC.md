# API 契约（规划与现状）

## 1. 说明

仓库内包含 API Gateway 组件与路由定义，并提供了一个基于 aiohttp 的最小 HTTP Server（src/api_server/server.py），用于将真实 HTTP 请求转发到 APIGateway.handle_request。本文件用于定义对外契约口径，并标注实现要点与约束。

## 2. 统一响应格式（建议）

成功：

```json
{ "success": true, "data": { }, "timestamp": 1710000000.0 }
```

失败：

```json
{ "success": false, "error": { "code": "BAD_REQUEST", "message": "..." }, "timestamp": 1710000000.0 }
```

## 3. 端点清单（按路由定义）

### 3.1 健康检查

- GET /api/health
  - 返回：系统状态、uptime、版本等

### 3.2 专家列表

- GET /api/experts
  - 返回：已注册专家列表、supported_tasks、版本信息

### 3.3 单次处理

- POST /api/process
  - 请求体（建议）：

```json
{
  "text": "分析 600000.SH",
  "task_type": "stock_analysis",
  "context": { },
  "extra_params": { }
}
```

  - 返回（建议）：AggregatedResult（见 05_DATA_MODEL.md）

### 3.4 批量处理

- POST /api/batch
  - 请求体（建议）：

```json
{
  "requests": [
    { "text": "问题1", "task_type": "..." },
    { "text": "问题2", "task_type": "..." }
  ]
}
```

### 3.5 监控与配置（规划）

- GET /api/monitor/status
- GET /api/monitor/metrics
- GET /api/config
- POST /api/config
- GET /api/logs

### 3.6 投资组合（Portfolio）

- GET /api/portfolio/<user_id>
  - 返回：用户持仓列表（symbol/quantity/updated_at）
- POST /api/portfolio/<user_id>/positions
  - 请求体：{"symbol":"600000.SH","quantity":1000}
  - 说明：quantity=0 表示删除该持仓
- GET /api/portfolio/<user_id>/stats
  - 返回：positions_count、total_quantity、symbols

## 4. 现状差异与落地建议

- 实现要点：
  - 通过 OrchestratorFacade 适配编排器接口：process(text, task_type, context, user_id, extra_params) -> AggregatedResult(JSON)
  - 通过 APIGateway 支持路径参数（/api/experts/<name>）与统一响应封装
  - 统一数据模型：路由层输出 ExpertResult/AggregatedResult 的 JSON 形态，避免多套字段
