# Portfolio：数据口径与验收

## 1. 目标

- 提供一个最小可用的“持仓记录/查询/更新/统计”能力
- 支持落盘（默认 sqlite），用于后续复盘与扩展

## 2. 数据结构

### 2.1 Position

- symbol：股票/标的代码（字符串）
- quantity：数量（整数）
- updated_at：更新时间（ISO 字符串）

### 2.2 Portfolio

- user_id
- positions[]：Position 列表

### 2.3 Stats

- user_id
- positions_count
- total_quantity
- symbols[]

## 3. API 契约

- GET /api/portfolio/<user_id>
- POST /api/portfolio/<user_id>/positions
  - body：{"symbol":"600000.SH","quantity":100}
  - 说明：quantity=0 表示删除该 symbol
- GET /api/portfolio/<user_id>/stats

## 4. 验收用例

- 创建/更新持仓：
  - POST positions 写入后，GET portfolio 能读到对应 symbol 与 quantity
- 删除持仓：
  - quantity=0 后，stats.positions_count 递减
- 落盘一致性（sqlite/json）：
  - 重启服务后仍能读回数据（以 storage 配置为准）
