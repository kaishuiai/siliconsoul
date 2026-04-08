# 鉴权与用户体系（Token）

## 1. 目标

- 以最小成本提供 API 鉴权能力（Bearer Token）
- 将 user_id 绑定到请求上下文：Portfolio 与请求历史按 user_id 隔离
- 默认关闭鉴权，开启后需提供 tokens 映射

## 2. 鉴权规则

- Header：Authorization: Bearer <token>
- token -> user_id：由配置提供映射表
- auth.enabled=true 时：
  - 默认仅 /api/health、/api/me 免鉴权
  - 其它端点缺 token 或 token 无效返回 401
  - 访问 /api/portfolio/<user_id>、/api/history/<user_id> 时，路径 user_id 必须与 token 映射的 user_id 一致，否则 403

## 3. 配置

config/default.json：

- auth.enabled：是否启用
- auth.tokens：token->user_id 映射
- auth.exempt_paths：免鉴权路径列表

环境变量覆盖（推荐用于生产）：

- SILICONSOUL_AUTH_ENABLED=true|false
- SILICONSOUL_API_TOKENS=token1:userA,token2:userB

## 4. 验收

- 未携带 token 访问受保护端点返回 401
- 携带有效 token 能访问 /api/portfolio 与 /api/history 且只读写自己的数据
- 无效 token 或越权访问返回 403/401
