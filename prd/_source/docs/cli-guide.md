# SiliconSoul CLI 指南

**版本**: v1.1.0  
**最后更新**: 2026-04-06

## 📋 概述

SiliconSoul CLI 提供了完整的命令行界面，用于：
- 列举和管理Expert
- 执行单个Expert任务
- 通过MOE编排器处理请求
- 批量处理多个请求
- 系统健康检查和监控

## 🚀 安装和使用

### 快速开始

```bash
# 查看帮助
./siliconsoul --help

# 显示版本
./siliconsoul --version

# 系统信息
./siliconsoul info

# 健康检查
./siliconsoul health-check
```

### 输出格式

```bash
# JSON格式（默认）
./siliconsoul list-experts

# 文本格式
./siliconsoul --format text list-experts

# 详细模式
./siliconsoul --verbose list-experts
```

## 📚 命令参考

### 1. list-experts - 列出所有Expert

**用途**: 显示所有已注册的Expert及其信息

```bash
# 列出所有Expert
./siliconsoul list-experts

# 输出示例
{
  "status": "success",
  "data": [
    {
      "name": "StockAnalysisExpert",
      "version": "1.0",
      "supported_tasks": [
        "stock_analysis",
        "technical_analysis"
      ],
      "performance": {
        "call_count": 42,
        "error_rate": 0.0,
        "avg_duration_ms": 125.5
      }
    },
    ...
  ],
  "message": "Total: 9 experts"
}
```

### 2. run-expert - 执行特定Expert

**用途**: 运行指定的Expert处理输入

```bash
# 基础用法
./siliconsoul run-expert \
  --expert StockAnalysisExpert \
  --input "AAPL stock analysis"

# 指定用户ID
./siliconsoul run-expert \
  --expert DialogExpert \
  --input "Hello, how are you?" \
  --user-id user_123

# 传递上下文
./siliconsoul run-expert \
  --expert StockAnalysisExpert \
  --input "AAPL" \
  --context '{"market":"US","period":"1Y"}'

# 输出示例
{
  "status": "success",
  "data": {
    "expert": "DialogExpert",
    "result": {
      "user_message": "Hello",
      "intent": "greeting",
      "sentiment": "positive",
      "response": "Hello! How can I help?"
    },
    "confidence": 0.95,
    "error": null
  }
}
```

**参数**:
- `--expert` (必需) - Expert名称
- `--input` (必需) - 输入文本
- `--user-id` (可选) - 用户ID，默认: cli_user
- `--context` (可选) - JSON格式的上下文

**支持的Expert**:
- DemoExpert1, DemoExpert2, DemoExpert3
- StockAnalysisExpert
- KnowledgeExpert
- DialogExpert
- DecisionExpert
- ReflectionExpert
- ExecutionExpert

### 3. process - 通过MOE处理请求

**用途**: 通过MOE编排器处理请求，自动选择合适的Expert

```bash
# 处理单个请求
./siliconsoul process \
  --request '{"text":"分析苹果股票","user_id":"user1","context":{}}'

# 复杂请求示例
./siliconsoul process \
  --request '{
    "text": "What is the technical analysis of TSLA?",
    "user_id": "analyst_123",
    "context": {
      "market": "US",
      "timeframe": "daily"
    }
  }'

# 输出示例
{
  "status": "success",
  "data": {
    "status": "processed",
    "results": [...],
    "aggregated": {
      "overall_analysis": "...",
      "confidence": 0.92
    }
  }
}
```

### 4. batch - 批量处理请求

**用途**: 从JSON文件批量处理多个请求

```bash
# 批量处理
./siliconsoul batch --file requests.json

# 输出示例
{
  "status": "success",
  "data": {
    "total": 3,
    "processed": 3,
    "results": [
      {
        "request": {...},
        "result": {...}
      },
      ...
    ]
  },
  "message": "Processed 3 requests"
}
```

**请求文件格式** (requests.json):
```json
[
  {
    "text": "Analyze AAPL",
    "user_id": "user1"
  },
  {
    "text": "What is AI?",
    "user_id": "user2"
  },
  {
    "text": "Make a decision",
    "user_id": "user3",
    "context": {"options": ["A", "B"]}
  }
]
```

### 5. health-check - 系统健康检查

**用途**: 检查系统和所有Expert的健康状态

```bash
# 运行健康检查
./siliconsoul health-check

# 输出示例
{
  "status": "success",
  "data": {
    "status": "healthy",
    "experts_count": 9,
    "experts": [
      {
        "name": "StockAnalysisExpert",
        "healthy": true,
        "calls": 42
      },
      ...
    ],
    "version": "1.1.0"
  },
  "message": "System is healthy"
}
```

### 6. version - 显示版本信息

**用途**: 显示系统版本和覆盖率信息

```bash
# 显示版本
./siliconsoul version

# 输出示例
{
  "status": "success",
  "data": {
    "version": "1.1.0",
    "experts": 9,
    "test_coverage": "81.39%"
  }
}
```

### 7. info - 系统信息

**用途**: 显示系统详细信息和功能列表

```bash
# 显示系统信息
./siliconsoul info

# 输出示例
{
  "status": "success",
  "data": {
    "name": "SiliconSoul MOE",
    "version": "1.1.0",
    "description": "Mixture of Experts Framework...",
    "experts_registered": 9,
    "experts_list": [...],
    "features": [...]
  }
}
```

### 8. config - 配置信息

**用途**: 显示当前系统配置

```bash
# 显示配置
./siliconsoul config

# 输出示例
{
  "status": "success",
  "data": {
    "timeout": 5.0,
    "experts_registered": 9,
    "output_format": "json"
  }
}
```

## 🔧 高级用法

### 与OpenClaw集成

```bash
# OpenClaw可以通过exec工具调用SiliconSoul
openclaw exec siliconsoul list-experts

# 使用JSON格式便于解析
openclaw exec siliconsoul --format json process \
  --request '{"text":"...","user_id":"..."}'
```

### 与脚本集成

```bash
#!/bin/bash

# 处理多个请求
for query in "AAPL" "TSLA" "MSFT"; do
  result=$(./siliconsoul run-expert \
    --expert StockAnalysisExpert \
    --input "$query" \
    --format json)
  
  # 解析JSON结果
  confidence=$(echo $result | jq '.data.confidence')
  echo "Query: $query, Confidence: $confidence"
done
```

### 错误处理

所有错误都返回统一格式：

```json
{
  "status": "error",
  "message": "Error description",
  "code": 1
}
```

**常见错误码**:
- `1` - 一般错误
- `2` - 参数错误
- `3` - Expert未找到
- `4` - 处理失败

## 📊 使用示例

### 场景1: 股票分析流程

```bash
# 1. 检查系统状态
./siliconsoul health-check

# 2. 列出可用Expert
./siliconsoul list-experts | grep StockAnalysisExpert

# 3. 分析股票
./siliconsoul run-expert \
  --expert StockAnalysisExpert \
  --input "AAPL" \
  --context '{"period":"1Y","market":"US"}'
```

### 场景2: 对话系统

```bash
# 对话Expert
./siliconsoul run-expert \
  --expert DialogExpert \
  --input "What is machine learning?" \
  --user-id analyst_001
```

### 场景3: 批量决策支持

创建 decisions.json:
```json
[
  {
    "text": "Should we invest in TSLA?",
    "user_id": "pm_001",
    "context": {"budget": 1000000}
  },
  {
    "text": "Product A or B?",
    "user_id": "pm_002"
  }
]
```

运行：
```bash
./siliconsoul batch --file decisions.json > decisions_output.json
```

## 🔐 安全考虑

- CLI不存储任何凭证或密钥
- 所有输入都经过验证
- 输出中不包含敏感信息
- 建议在生产环境使用环境变量配置

## 📈 性能提示

- **单Expert**: ~100-500ms
- **批量处理**: ~1-2s 每个请求
- **并行执行**: MOE框架自动优化

## 🐛 故障排查

### 命令不存在
```bash
# 检查CLI是否可执行
ls -la siliconsoul

# 确保在项目根目录
cd /path/to/siliconsoul-moe
```

### Expert未找到
```bash
# 先列出所有Expert
./siliconsoul list-experts

# 使用正确的Expert名称
```

### 解析错误
```bash
# 验证JSON格式
echo '{"text":"test"}' | python3 -m json.tool

# 传递正确的JSON
```

## 📝 文件位置

```
siliconsoul-moe/
├── siliconsoul           # 可执行脚本
├── src/cli/
│   ├── __init__.py
│   └── main.py           # CLI实现
└── tests/unit/
    └── test_cli.py       # CLI测试
```

## 🔗 相关文档

- [README.md](../README.md) - 项目概述
- [VERSIONING.md](../VERSIONING.md) - 版本管理
- [API参考](./api.md) - API详细文档

## 📞 支持

如有问题或建议，请联系开发团队。

---

**版本**: v1.1.0  
**最后更新**: 2026-04-06  
**作者**: CC (SiliconSoul Developer)
