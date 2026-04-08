# SiliconSoul MOE - Architecture Guide

## System Overview

The Mixture of Experts (MOE) system is built on a 4-layer architecture:

```
Layer 4: User Interface
    ↓
Layer 3: Coordination Layer (Task Classifier → Expert Router)
    ↓
Layer 2: Expert Layer (6 specialized experts in parallel)
    ↓
Layer 1: Tool Layer (External APIs, Knowledge Base, etc.)
```

## Core Components

### 1. MOEOrchestrator
**Purpose**: Central coordinator for the entire system

**Responsibilities**:
- Register and manage experts
- Execute experts in parallel
- Aggregate results
- Handle timeouts

**Key Methods**:
- `register_expert(expert)`: Add a new expert
- `execute_experts_parallel(names, request)`: Run multiple experts concurrently
- `process_request(request)`: Full pipeline execution

**Code Location**: `src/core/moe_orchestrator.py`

### 2. Expert Base Class
**Purpose**: Define the interface all experts must follow

**Key Properties**:
- `name`: Expert identifier
- `version`: Version number
- `get_supported_tasks()`: List of task types this expert handles

**Key Methods**:
- `async analyze(request)`: Core analysis method (abstract)
- `async execute(request, timeout)`: Execution with timeout and error handling
- `get_metadata()`: Return capability description
- `get_performance_stats()`: Return performance metrics

**Code Location**: `src/experts/expert_base.py`

### 3. Data Models (Pydantic)
**Purpose**: Ensure type safety and data validation

**Models**:

#### ExpertRequest
Input format with:
- `text`: User input
- `user_id`: User identifier
- `context`: Conversation history (optional)
- `task_type`: Pre-classified task type (optional)
- `extra_params`: Additional parameters

#### ExpertResult
Output format with:
- `expert_name`: Which expert produced this
- `result`: Analysis result (dict)
- `confidence`: Confidence score (0-1)
- `metadata`: Additional info (version, execution details)
- `timestamp_start/end`: Timing information
- `error`: Error message if failed

#### AggregatedResult
Final combined output with:
- `final_result`: Merged conclusion
- `expert_results`: All individual results
- `overall_confidence`: Average confidence
- `consensus_level`: Agreement level (high/medium/low)

**Code Location**: `src/models/request_response.py`

### 4. Task Classifier
**Purpose**: Automatically identify task type from user input

**Supported Tasks** (Phase 1):
- `stock_analysis`: Stock recommendation
- `knowledge_query`: Information retrieval
- `conversation`: General dialog
- `decision_support`: Complex decision making
- `reflection`: System self-analysis

**Code Location**: `src/core/task_classifier.py` (Phase 2)

### 5. Expert Router
**Purpose**: Select appropriate experts for a task

**Strategy**:
- Rule-based routing (Phase 1)
- ML-based routing (Phase 2+)

**Routing Table** (Phase 1):
- `stock_analysis` → StockExpert + AnalysisExpert
- `knowledge_query` → KnowledgeExpert
- `conversation` → DialogExpert
- `decision_support` → DecisionExpert + ReflectionExpert
- Default → All available experts

**Code Location**: `src/core/expert_router.py` (Phase 2)

### 6. Result Aggregator
**Purpose**: Combine multiple expert results intelligently

**Aggregation Strategies** (Phase 1):
- Average confidence scores
- Consensus level detection
- Conflict resolution

**Code Location**: `src/core/result_aggregator.py` (Phase 2)

## Execution Flow

### Standard Pipeline

```
1. User sends request
   └─ Input: Text + User ID
   
2. Task Classification
   └─ Identify task type (stock, knowledge, etc.)
   
3. Expert Selection
   └─ Choose relevant experts based on task
   
4. Parallel Execution
   └─ All selected experts run concurrently
      └─ Each has 2s timeout
      └─ Auto error handling
      └─ Performance monitoring
   
5. Result Aggregation
   └─ Combine results
   └─ Calculate consensus
   └─ Detect conflicts
   
6. Response to User
   └─ Output: Final decision + reasoning
```

## Concurrency Model

**Technology**: Python asyncio (async/await)

**Benefits**:
- Non-blocking I/O
- True parallelism for I/O-bound operations
- Low memory overhead compared to threading

**Example**:
```
Task Timeline:
Time 0ms:   Start ────┐
                      ├─ Expert1 (0-500ms)
Time 500ms:           ├─ Expert2 (0-600ms)
                      ├─ Expert3 (0-400ms)
Time 600ms: Complete
                      Total: 600ms (vs 1500ms sequential)
```

## Error Handling

**Strategy**: Graceful degradation

1. **Expert Timeout** (2s)
   - Expert returns error result
   - Other experts continue
   - System continues with remaining results

2. **Expert Crash**
   - Caught by wrapper
   - Returns error result with exception message
   - No impact on other experts

3. **All Experts Fail**
   - System returns aggregated error
   - User sees fallback message

## Performance Characteristics

### Timing Targets (Phase 1)
- Task Classification: 10ms
- Expert Selection: 5ms
- Parallel Execution: 500-600ms (3 experts @ 2s timeout)
- Aggregation: 20ms
- **Total: ~650ms**

### Memory
- Base: ~50MB (Python + libraries)
- Per Request: ~5MB (temporary)
- Per Expert: ~10MB (model + state)
- **Total for 6 experts: ~150MB**

### Throughput
- Single machine: 150+ requests/sec
- Scaling: Linear with number of machines

## Integration Points

### External Systems

1. **Feishu API**
   - Send notifications
   - Retrieve user info
   - Access knowledge base

2. **Tushare API**
   - Stock data (real-time prices)
   - Technical indicators
   - Company fundamentals

3. **Knowledge Base**
   - Wikipedia, research papers
   - Internal knowledge
   - Custom documents

4. **LLMs**
   - Dialog expert
   - Text analysis
   - Reflection

## Security Model

**Data Flow**:
```
User Request (local)
    ↓ (sanitize)
Expert Processing (internal)
    ↓ (log)
Result Aggregation (internal)
    ↓ (format)
Response (local or external)
```

**Key Principles**:
- No sensitive data in logs
- Timeout prevents hanging
- Error messages are safe
- Rate limiting for external APIs

## Testing Strategy

### Unit Tests
- Individual expert functionality
- Data model validation
- Aggregation logic

### Integration Tests
- Full pipeline execution
- Multi-expert scenarios
- Error scenarios

### Load Tests
- Throughput validation
- Memory profiling
- Timeout behavior

## Future Enhancements

### Phase 2+
- ML-based task classification
- Dynamic expert selection
- Adaptive timeouts
- Result caching
- Expert performance tracking
- A/B testing framework

## References

- [Data Models](../src/models/request_response.py)
- [Expert Base Class](../src/experts/expert_base.py)
- [MOE Orchestrator](../src/core/moe_orchestrator.py)
- [API Reference](./api.md)
