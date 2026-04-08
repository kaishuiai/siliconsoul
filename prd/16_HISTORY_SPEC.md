# 请求历史与复盘

## 1. 目标

- 每次 /api/process、/api/batch、/api/analysis/analyze 等请求都落盘
- 支持按 user_id 查询历史列表与查看详情（请求+专家输出）
- 前端提供列表检索与详情回放

## 2. 落盘内容（最小集合）

- request：request_id、user_id、text、timestamp、context
- results：每个专家的 expert_name、result、confidence、duration_ms、error
- aggregated：以 __aggregated__ 记录整体 summary（final_result、overall_confidence、consensus_level）

## 3. API 契约

- GET /api/history/<user_id>?q=&limit=&offset=
  - 返回 items[]：request_id、user_id、text、timestamp
- GET /api/history/<user_id>/<request_id>
  - 返回 request + results[]

## 4. 前端

- History 页面：
  - 支持关键词搜索（q）
  - 点击列表项加载详情
  - 详情展示每个专家的结构化输出与错误

## 5. 验收

- 发起任意分析请求后，History 列表中出现对应记录
- 点击记录可回放专家结果与最终 summary
- 鉴权开启时仅能看到自身 user_id 记录
- 批量请求（/api/batch）中每条子请求都生成独立 request_id，并可在 History 中逐条回放
