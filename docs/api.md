# SiliconSoul MOE - API Reference

## Overview

Complete API documentation for SiliconSoul MOE system.

## HTTP API Server

本仓库提供一个基于 aiohttp 的最小 HTTP API Server（用于对外提供 /api/* 端点）。

启动方式：

```bash
python -m src.api_server.server
```

环境变量：

- CONFIG_FILE：配置文件路径（默认使用 ConfigManager 内置默认值；docker-compose 默认设置为 config/default.yaml）
- HOST：监听地址（默认 0.0.0.0）
- PORT：监听端口（默认 8000）

常用端点：

- GET /api/health
- GET /api/experts
- GET /api/experts/<name>
- POST /api/uploads
- POST /api/process
- POST /api/batch
- GET /api/monitor/metrics
- GET /api/monitor/status
- GET /api/monitor/stats
- GET /api/config
- POST /api/config
- GET /api/portfolio/<user_id>
- POST /api/portfolio/<user_id>/positions
- GET /api/portfolio/<user_id>/stats
- GET /api/me
- GET /api/history/<user_id>
- GET /api/history/<user_id>/<request_id>

### POST /api/uploads

- Content-Type: multipart/form-data
- 字段：file（可重复多次，表示多文件）
- 返回：data.files[] = {file_id, original_name}

### GET /api/history/<user_id>

支持过滤参数（query string）：

- q：按请求文本关键词
- expert_name：按专家结果过滤（例如 CFOExpert）
- task_type：按任务类型过滤（例如 cfo_chat）
- conversation_id：按会话 ID 过滤（用于聊天会话聚合）
- replay_of：按重放父请求 ID 过滤
- only_replay：true/false，仅查看重放产生的请求
- consensus_level：high/medium/low/none
- only_errors：true/false
- since/until：ISO 时间范围

### GET /api/history/roots/<user_id>

返回字段：

- items：按 root 聚合的请求链摘要（latest_request_id/latest_timestamp/total_nodes/replay_nodes/max_depth）
- total_roots：根请求总数

支持参数：

- sort_by：latest/risk/depth/activity

其中 items 每项包含：

- risk_score：链路风险评分（用于工作台排序）
- risk_reasons：风险评分解释标签列表
- suggested_actions：快速处置动作建议列表

### GET /api/history/<user_id>/<request_id>

返回字段（兼容模式）：

- request：请求记录
- results：原始结果记录（兼容老结构）
- aggregated：聚合记录（兼容老结构）
- expert_results：标准化专家结果（对齐 process 输出）
- result：标准化聚合结果（对齐 process 输出）

### GET /api/history/<user_id>/<request_id>/chain

返回字段：

- request_id：当前请求 ID
- root_id：链路根请求 ID
- lineage：从根到当前的线性链路
- descendants：从根向下的后代请求（按时间排序）
- stats：链路统计（节点数、深度、一致性分布、置信度极值节点）

### POST /api/process

返回字段（统一模型）：

- request_id：请求 ID（可用于 history/replay）
- final_result：聚合结论对象
- expert_results：专家结果数组（含 timestamp_start/timestamp_end/error）
- overall_confidence / consensus_level / duration_ms / num_experts

### POST /api/process/stream

- Content-Type: `text/event-stream`
- 事件：`start` / `delta` / `done` / `error`
- 说明：服务端流式返回文本增量（前端可实现 token 级实时渲染）

### POST /api/history/<user_id>/<request_id>/replay

返回字段（兼容模式）：

- request_id / final_result / expert_results（统一字段）

### POST /api/batch

返回字段（兼容模式）：

- summary：{total, success, failed, avg_duration_ms}
- items：逐条处理结果（成功项含 data，失败项含 error，彼此隔离）
- results：兼容字段（success/error 扁平列表）

### 响应 envelope（兼容模式）

当前后端会同时返回以下字段以兼容新旧客户端：

- success: true/false
- status: success/error
- data（成功时）
- error/code/message（失败时）
- timestamp（unix float）与 timestamp_iso（ISO 字符串）

## Table of Contents
1. [MOEOrchestrator](#moeorchestrator)
2. [Expert](#expert)
3. [Data Models](#data-models)
4. [Error Handling](#error-handling)

---

## MOEOrchestrator

### Constructor

```python
MOEOrchestrator(default_timeout_sec: float = 2.0)
```

**Parameters**:
- `default_timeout_sec`: Default timeout for each expert (seconds)

**Example**:
```python
moe = MOEOrchestrator(default_timeout_sec=2.0)
```

### Methods

#### register_expert

```python
def register_expert(self, expert: Expert) -> None
```

Register a new expert with the system.

**Parameters**:
- `expert`: Expert instance

**Raises**:
- `ValueError`: If expert with same name already registered

**Example**:
```python
moe.register_expert(StockAnalysisExpert())
```

#### get_expert

```python
def get_expert(self, name: str) -> Optional[Expert]
```

Retrieve a registered expert by name.

**Parameters**:
- `name`: Expert name

**Returns**: Expert instance or None

**Example**:
```python
expert = moe.get_expert("StockAnalysisExpert")
```

#### get_available_experts

```python
def get_available_experts(self) -> List[str]
```

Get list of all registered expert names.

**Returns**: List of expert names

**Example**:
```python
names = moe.get_available_experts()
# ["Expert1", "Expert2", "Expert3"]
```

#### execute_experts_parallel

```python
async def execute_experts_parallel(
    expert_names: List[str],
    request: ExpertRequest,
    timeout_sec: Optional[float] = None
) -> List[ExpertResult]
```

Execute multiple experts in parallel.

**Parameters**:
- `expert_names`: Names of experts to execute
- `request`: User request
- `timeout_sec`: Overall timeout (optional)

**Returns**: List of ExpertResult objects

**Example**:
```python
results = await moe.execute_experts_parallel(
    ["Expert1", "Expert2"],
    request
)
```

#### process_request

```python
async def process_request(
    request: ExpertRequest,
    expert_names: Optional[List[str]] = None,
    timeout_sec: Optional[float] = None
) -> AggregatedResult
```

Process a user request through the full MOE pipeline.

**Parameters**:
- `request`: User request object
- `expert_names`: Specific experts to use (None = all)
- `timeout_sec`: Execution timeout

**Returns**: AggregatedResult with final decision

**Example**:
```python
request = ExpertRequest(text="analysis...", user_id="user1")
result = await moe.process_request(request)
```

---

## Expert

### Base Class Definition

```python
class Expert(ABC):
    """Base class for all experts"""
    
    def __init__(self, name: str, version: str = "1.0")
    async def analyze(self, request: ExpertRequest) -> ExpertResult
    async def execute(self, request: ExpertRequest, timeout_sec: float = 2.0) -> ExpertResult
    def get_metadata(self) -> Dict[str, Any]
    def get_supported_tasks(self) -> List[str]
    def get_performance_stats(self) -> Dict[str, Any]
```

### Creating Custom Experts

#### Step 1: Inherit from Expert

```python
from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, ExpertResult

class MyExpert(Expert):
    def __init__(self):
        super().__init__(name="MyExpert", version="1.0")
```

#### Step 2: Implement analyze()

```python
async def analyze(self, request: ExpertRequest) -> ExpertResult:
    """
    Your analysis logic here.
    MUST return ExpertResult.
    """
    try:
        # Your logic
        result = {...}
        confidence = 0.85
        
        return ExpertResult(
            expert_name=self.name,
            result=result,
            confidence=confidence,
            metadata={"version": self.version},
            timestamp_start=datetime.now().timestamp(),
            timestamp_end=datetime.now().timestamp(),
        )
    except Exception as e:
        return ExpertResult(
            expert_name=self.name,
            result={},
            confidence=0.0,
            timestamp_start=...,
            timestamp_end=...,
            error=str(e)
        )
```

#### Step 3: Override get_supported_tasks()

```python
def get_supported_tasks(self) -> List[str]:
    """Return list of task types this expert handles"""
    return ["my_task_type", "another_type"]
```

#### Step 4: Register with MOE

```python
moe = MOEOrchestrator()
moe.register_expert(MyExpert())
```

---

## Data Models

All models use Pydantic for validation.

### ExpertRequest

```python
class ExpertRequest(BaseModel):
    text: str                           # Required: user input
    user_id: str                        # Required: user identifier
    context: Optional[Dict[str, Any]]   # Optional: conversation history
    task_type: Optional[str]            # Optional: pre-classified task
    timestamp: float                    # Auto-set: request time
    extra_params: Optional[Dict]        # Optional: additional parameters
```

**Example**:
```python
request = ExpertRequest(
    text="What is the stock price of Apple?",
    user_id="user_123",
    context={"last_topic": "stocks"},
    task_type="stock_analysis"
)
```

### ExpertResult

```python
class ExpertResult(BaseModel):
    expert_name: str                    # Which expert produced this
    result: Dict[str, Any]              # Analysis result content
    confidence: float                   # Confidence score (0-1)
    metadata: Dict[str, Any]            # Additional metadata
    timestamp_start: float              # Start time
    timestamp_end: float                # End time
    error: Optional[str]                # Error message if failed
    
    @property
    def duration_ms(self) -> float
```

**Example**:
```python
result = ExpertResult(
    expert_name="StockExpert",
    result={"price": 150.25, "trend": "up"},
    confidence=0.92,
    metadata={"version": "1.0"},
    timestamp_start=1712462640.0,
    timestamp_end=1712462641.5
)

# Access duration
print(result.duration_ms)  # 1500.0
```

### AggregatedResult

```python
class AggregatedResult(BaseModel):
    final_result: Dict[str, Any]        # Merged conclusion
    expert_results: List[ExpertResult]  # All individual results
    overall_confidence: float           # Average confidence (0-1)
    num_experts: int                    # Number of experts used
    consensus_level: str                # "high", "medium", or "low"
    duration_ms: float                  # Total execution time
```

**Example**:
```python
aggregated = AggregatedResult(
    final_result={"decision": "BUY", "confidence": 0.93},
    expert_results=[...],
    overall_confidence=0.93,
    num_experts=3,
    consensus_level="high",
    duration_ms=620.0
)
```

---

## Error Handling

### Expert-Level Errors

Experts handle their own errors:

```python
try:
    # Your analysis
except Exception as e:
    return ExpertResult(..., error=str(e))
```

### System-Level Errors

The framework catches and logs:
- Timeouts
- Exceptions during parallel execution
- Invalid expert registrations

### Error Result Example

```python
{
    "expert_name": "MyExpert",
    "result": {},
    "confidence": 0.0,
    "error": "Expert timed out after 2.0s",
    "timestamp_start": 1712462640.0,
    "timestamp_end": 1712462642.0
}
```

### Checking for Errors

```python
result = await moe.process_request(request)

# Check if all experts succeeded
successful = [r for r in result.expert_results if not r.error]
failed = [r for r in result.expert_results if r.error]

if failed:
    print(f"Failed experts: {[r.expert_name for r in failed]}")
```

---

## Complete Example

```python
import asyncio
from src.core.moe_orchestrator import MOEOrchestrator
from src.experts.demo_expert_1 import DemoExpert1
from src.experts.demo_expert_2 import DemoExpert2
from src.models.request_response import ExpertRequest

async def main():
    # Initialize
    moe = MOEOrchestrator(default_timeout_sec=2.0)
    
    # Register experts
    moe.register_expert(DemoExpert1())
    moe.register_expert(DemoExpert2())
    
    # Create request
    request = ExpertRequest(
        text="Your question here",
        user_id="user_123"
    )
    
    # Process
    result = await moe.process_request(request)
    
    # Check results
    print(f"Overall confidence: {result.overall_confidence}")
    print(f"Consensus: {result.consensus_level}")
    print(f"Duration: {result.duration_ms}ms")
    
    # Inspect individual results
    for expert_result in result.expert_results:
        if expert_result.error:
            print(f"❌ {expert_result.expert_name}: {expert_result.error}")
        else:
            print(f"✓ {expert_result.expert_name}: {expert_result.result}")

# Run
asyncio.run(main())
```

---

## Best Practices

1. **Always return ExpertResult** - Never raise exceptions, return error field
2. **Set proper confidence** - Be conservative, avoid overconfidence
3. **Include metadata** - Track version and execution details
4. **Handle timeouts gracefully** - 2s timeout will be enforced
5. **Validate input** - Check request.text is not empty
6. **Document tasks** - List supported tasks clearly
7. **Monitor performance** - Use get_performance_stats()

---

Last Updated: 2026-04-07
