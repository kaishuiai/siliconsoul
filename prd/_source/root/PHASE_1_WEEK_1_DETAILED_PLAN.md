# Phase 1 Week 1 - MOE核心框架搭建 (详细任务分解)

**计划日期**: 2026-04-07 ~ 2026-04-13  
**工作量**: 2000行代码 (核心框架)  
**目标**: 完成MOE框架搭建和3个Demo专家实现  
**进度汇报**: 每2小时汇报一次工作进展

---

## 🎯 Week 1 总体目标

```
启动时: 2026-04-07 08:00 GMT+8
结束时: 2026-04-13 17:00 GMT+8

验收标准:
✅ MOE框架核心代码 (~1000行)
✅ 3个可运行的Demo专家
✅ 完整的单元测试 (>80%覆盖率)
✅ 完整的项目文档
✅ 性能基准基线
```

---

## 📋 Day 1 (Monday 04-07) - 项目初始化 (200行代码)

### 任务 1.1: 创建项目结构 (3小时)

**目标**: 建立标准的Python项目结构

```bash
创建的目录树:
siliconsoul-moe/
├── src/                           # 源代码目录
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── moe_orchestrator.py   # MOE编排器 (待实现)
│   │   ├── task_classifier.py    # 任务分类器 (待实现)
│   │   ├── expert_router.py      # 专家路由器 (待实现)
│   │   └── result_aggregator.py  # 结果聚合器 (待实现)
│   ├── experts/
│   │   ├── __init__.py
│   │   ├── expert_base.py        # Expert基类 (待实现)
│   │   ├── demo_expert_1.py      # Demo专家1
│   │   ├── demo_expert_2.py      # Demo专家2
│   │   └── demo_expert_3.py      # Demo专家3
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request_response.py   # 数据模型 (待实现)
│   │   └── confidence.py         # 置信度模型 (待实现)
│   └── utils/
│       ├── __init__.py
│       ├── logger.py             # 日志工具 (待实现)
│       └── helpers.py            # 辅助函数
├── tests/                         # 测试目录
│   ├── __init__.py
│   ├── conftest.py              # pytest配置
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_expert_base.py
│   │   ├── test_moe_orchestrator.py
│   │   └── test_models.py
│   └── integration/
│       ├── __init__.py
│       └── test_full_pipeline.py
├── docs/                         # 文档目录
│   ├── architecture.md
│   ├── api.md
│   └── development.md
├── config/                       # 配置目录
│   ├── default.yaml
│   └── router_rules.yaml
├── scripts/                      # 脚本目录
│   ├── run_tests.sh
│   └── benchmark.py
├── requirements.txt              # Python依赖
├── pytest.ini                    # pytest配置
├── .gitignore                    # Git忽略规则
└── README.md                     # 项目说明
```

**具体步骤**:
1. 创建所有目录和 `__init__.py` 文件
2. 创建 `.gitignore` 文件 (Python标准)
3. 创建 `requirements.txt` 初始版本
4. 创建 `README.md` 基础版本

**验收标准**:
- [ ] 目录结构按上述创建完成
- [ ] 所有必要的 `__init__.py` 文件存在
- [ ] 可以运行 `python -m pytest` (虽然还没有测试)

**预计代码量**: ~100行 (配置文件)

---

### 任务 1.2: 设置开发基础设施 (2小时)

**目标**: 建立自动化工具链

**要做的事**:

1. **requirements.txt** (Python依赖)
```
# 核心依赖
pydantic==2.5.0          # 数据模型
pytest==7.4.3            # 单元测试
pytest-asyncio==0.21.1   # 异步测试支持
pytest-cov==4.1.0        # 覆盖率报告

# 开发工具
black==23.12.0           # 代码格式化
pylint==3.0.3            # 代码检查
mypy==1.7.1              # 静态类型检查

# 数据科学
numpy==2.0.2
pandas==2.3.3
scikit-learn==1.6.1

# 日志和监控
python-logging==0.5.1.2  # 扩展日志功能
```

2. **pytest.ini** (配置pytest)
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --cov=src
    --cov-report=html
    --cov-report=term-missing
```

3. **.gitignore** (标准Python)
```
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
dist/
build/
.venv/
venv/
*.log
.DS_Store
```

4. **setup.py** 或 **pyproject.toml** (可选)

**验收标准**:
- [ ] 能运行 `pip install -r requirements.txt`
- [ ] 能运行 `python -m pytest` (显示配置正确)
- [ ] IDE能识别项目结构

**预计代码量**: ~50行

---

### 任务 1.3: 编写项目文档框架 (2小时)

**目标**: 建立清晰的文档基础

**要做的文件**:

1. **README.md** (项目总览)
2. **docs/architecture.md** (架构说明)
3. **docs/api.md** (API参考)
4. **docs/development.md** (开发指南)

**README.md 内容**:
```markdown
# SiliconSoul MOE v2.0

Mixture of Experts 框架 for 智能决策支持系统

## 快速开始
## 核心功能
## 架构设计
## 开发指南
## 测试
## 部署
## 参考文档
```

**验收标准**:
- [ ] README内容清晰
- [ ] API文档框架完整
- [ ] 开发指南有具体示例

**预计代码量**: ~400行 (文档)

---

## 📋 Day 2-3 (Tue-Wed 04-08 ~ 04-09) - 数据模型和基础类 (500行代码)

### 任务 2.1: 实现数据模型 (Pydantic) (1.5天)

**目标**: 定义统一的请求/响应数据结构

**文件**: `src/models/request_response.py` (~250行)

**关键类定义**:

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class ExpertRequest(BaseModel):
    """专家请求模型 - 统一的输入格式"""
    
    # 核心字段
    text: str = Field(..., description="用户输入文本", min_length=1, max_length=10000)
    user_id: str = Field(..., description="用户ID")
    
    # 可选字段
    context: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="对话上下文 (历史消息)"
    )
    task_type: Optional[str] = Field(
        default=None,
        description="已分类的任务类型"
    )
    timestamp: float = Field(
        default_factory=lambda: datetime.now().timestamp(),
        description="请求时间戳"
    )
    extra_params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="额外参数 (扩展用)"
    )
    
    class Config:
        # JSON schema 生成
        json_schema_extra = {
            "example": {
                "text": "这个股票怎么样?",
                "user_id": "user_123",
                "context": {"last_topic": "stocks"},
                "timestamp": 1712462640.0
            }
        }

class ExpertResult(BaseModel):
    """专家结果模型 - 统一的输出格式"""
    
    # 核心字段
    expert_name: str = Field(..., description="专家名称")
    result: Dict[str, Any] = Field(..., description="分析结果内容")
    
    # 元数据
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="置信度 0-1"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="元数据 (版本/耗时等)"
    )
    
    # 时间信息
    timestamp_start: float = Field(..., description="开始时间戳")
    timestamp_end: float = Field(..., description="完成时间戳")
    
    # 错误处理
    error: Optional[str] = Field(
        default=None,
        description="错误信息 (若有)"
    )
    
    @property
    def duration_ms(self) -> float:
        """执行耗时 (毫秒)"""
        return (self.timestamp_end - self.timestamp_start) * 1000
    
    class Config:
        json_schema_extra = {
            "example": {
                "expert_name": "StockAnalysisExpert",
                "result": {
                    "score": 7.5,
                    "signal": "BUY",
                    "confidence": 0.85
                },
                "confidence": 0.92,
                "metadata": {"version": "1.0"},
                "timestamp_start": 1712462640.0,
                "timestamp_end": 1712462641.5,
            }
        }

class AggregatedResult(BaseModel):
    """聚合结果模型 - 多个专家结果的合并"""
    
    # 聚合结果
    final_result: Dict[str, Any] = Field(..., description="最终聚合结果")
    
    # 来源
    expert_results: List[ExpertResult] = Field(
        ...,
        description="所有专家的结果"
    )
    
    # 聚合统计
    overall_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="整体置信度"
    )
    num_experts: int = Field(..., description="参与的专家数量")
    consensus_level: str = Field(..., description="一致性等级 (high/medium/low)")
    
    # 时间信息
    duration_ms: float = Field(..., description="总耗时")
    
    class Config:
        json_schema_extra = {
            "example": {
                "final_result": {
                    "recommendation": "BUY",
                    "reasoning": "所有专家一致同意"
                },
                "expert_results": [],  # 省略
                "overall_confidence": 0.93,
                "num_experts": 3,
                "consensus_level": "high",
                "duration_ms": 420.0
            }
        }
```

**验收标准**:
- [ ] 三个主要模型定义清晰
- [ ] 所有字段都有类型和描述
- [ ] JSON schema示例准确
- [ ] 模型可序列化反序列化

**预计代码量**: 250行

---

### 任务 2.2: 实现Expert基类 (2天)

**目标**: 定义所有专家都要遵循的基类

**文件**: `src/experts/expert_base.py` (~250行)

**关键代码**:

```python
from abc import ABC, abstractmethod
from src.models.request_response import ExpertRequest, ExpertResult
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class Expert(ABC):
    """
    所有专家的抽象基类。
    
    每个具体的专家（股票分析、知识检索等）都应该继承此类
    并实现 analyze() 方法。
    
    特点:
    - 支持异步执行 (async def analyze)
    - 统一的输入/输出格式
    - 自动错误处理和日志记录
    - 性能监控 (耗时统计)
    """
    
    def __init__(self, name: str, version: str = "1.0"):
        """
        初始化专家。
        
        Args:
            name: 专家名称 (例如 "StockAnalysisExpert")
            version: 版本号 (例如 "1.0")
        """
        self.name = name
        self.version = version
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self._stats = {
            "call_count": 0,
            "error_count": 0,
            "total_duration_ms": 0.0,
        }
    
    @abstractmethod
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """
        核心分析方法 - 子类必须实现。
        
        Args:
            request: 专家请求 (包含用户输入、上下文等)
        
        Returns:
            ExpertResult: 分析结果
        
        说明:
            - 必须实现为 async 函数
            - 必须返回 ExpertResult 类型
            - 应该在内部处理异常，返回 error 字段
            - 执行时间应该<2秒 (否则MOE会超时)
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取专家的能力描述 (元数据)。
        
        Returns:
            Dict 包含:
            - name: 专家名称
            - version: 版本号
            - description: 专家描述
            - supported_tasks: 支持的任务类型
            - performance: 性能指标
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.__class__.__doc__ or "",
            "supported_tasks": self.get_supported_tasks(),
            "performance": self.get_performance_stats(),
        }
    
    def get_supported_tasks(self) -> list:
        """
        获取该专家支持的任务类型。
        
        Returns:
            List[str]: 支持的任务类型 (例如 ["stock_analysis", "recommendation"])
        
        子类应该重写此方法。
        """
        return []
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        avg_duration = (
            self._stats["total_duration_ms"] / self._stats["call_count"]
            if self._stats["call_count"] > 0
            else 0
        )
        return {
            "call_count": self._stats["call_count"],
            "error_count": self._stats["error_count"],
            "avg_duration_ms": round(avg_duration, 2),
            "error_rate": (
                self._stats["error_count"] / self._stats["call_count"]
                if self._stats["call_count"] > 0
                else 0
            ),
        }
    
    async def execute(self, request: ExpertRequest, timeout_sec: float = 2.0) -> ExpertResult:
        """
        执行分析 - 带有自动错误处理和性能监控。
        
        这是框架调用专家的入口点。不应该被子类覆盖。
        
        Args:
            request: 请求
            timeout_sec: 超时时间 (默认2秒)
        
        Returns:
            ExpertResult: 分析结果 (失败时包含error字段)
        """
        timestamp_start = datetime.now().timestamp()
        self._stats["call_count"] += 1
        
        try:
            # 调用子类的分析方法，带超时控制
            result = await asyncio.wait_for(
                self.analyze(request),
                timeout=timeout_sec
            )
            
            # 更新统计
            timestamp_end = datetime.now().timestamp()
            result.timestamp_end = timestamp_end
            
            duration_ms = (timestamp_end - timestamp_start) * 1000
            self._stats["total_duration_ms"] += duration_ms
            
            self.logger.info(
                f"Expert {self.name} succeeded in {duration_ms:.2f}ms"
            )
            
            return result
            
        except asyncio.TimeoutError:
            self._stats["error_count"] += 1
            timestamp_end = datetime.now().timestamp()
            
            self.logger.error(f"Expert {self.name} timed out after {timeout_sec}s")
            
            return ExpertResult(
                expert_name=self.name,
                result={},
                confidence=0.0,
                timestamp_start=timestamp_start,
                timestamp_end=timestamp_end,
                error=f"Expert timed out after {timeout_sec}s",
            )
            
        except Exception as e:
            self._stats["error_count"] += 1
            timestamp_end = datetime.now().timestamp()
            
            self.logger.error(f"Expert {self.name} failed: {str(e)}", exc_info=True)
            
            return ExpertResult(
                expert_name=self.name,
                result={},
                confidence=0.0,
                timestamp_start=timestamp_start,
                timestamp_end=timestamp_end,
                error=f"Expert error: {str(e)}",
            )
```

**验收标准**:
- [ ] 抽象基类定义清晰
- [ ] analyze() 方法被定义为抽象
- [ ] execute() 方法包含超时和错误处理
- [ ] 性能统计机制工作正常

**预计代码量**: 250行

---

## 📋 Day 4-5 (Thu-Fri 04-10 ~ 04-11) - MOE核心编排器 (400行代码)

### 任务 3.1: 实现MOE编排器 (2天)

**目标**: 实现核心的并行执行和编排逻辑

**文件**: `src/core/moe_orchestrator.py` (~400行)

**关键代码框架**:

```python
import asyncio
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, ExpertResult, AggregatedResult

logger = logging.getLogger(__name__)

class MOEOrchestrator:
    """
    MOE系统的核心编排器。
    
    职责:
    1. 管理Expert的注册和加载
    2. 执行多个Expert的并行任务
    3. 聚合结果
    4. 处理超时和失败
    """
    
    def __init__(self, default_timeout_sec: float = 2.0):
        """
        初始化编排器。
        
        Args:
            default_timeout_sec: 默认超时时间
        """
        self.experts: Dict[str, Expert] = {}
        self.default_timeout_sec = default_timeout_sec
        self.logger = logging.getLogger(__name__)
    
    def register_expert(self, expert: Expert) -> None:
        """
        注册一个专家。
        
        Args:
            expert: Expert实例
        
        Raises:
            ValueError: 如果同名专家已存在
        """
        if expert.name in self.experts:
            raise ValueError(f"Expert '{expert.name}' already registered")
        
        self.experts[expert.name] = expert
        self.logger.info(f"Registered expert: {expert.name}")
    
    def get_expert(self, name: str) -> Optional[Expert]:
        """获取已注册的专家"""
        return self.experts.get(name)
    
    def get_available_experts(self) -> List[str]:
        """获取所有已注册的专家名称"""
        return list(self.experts.keys())
    
    async def execute_experts_parallel(
        self,
        expert_names: List[str],
        request: ExpertRequest,
        timeout_sec: Optional[float] = None
    ) -> List[ExpertResult]:
        """
        并行执行多个专家。
        
        Args:
            expert_names: 要执行的专家名称列表
            request: 请求对象
            timeout_sec: 总超时时间 (可选)
        
        Returns:
            List[ExpertResult]: 所有完成的专家结果
        
        说明:
            - 所有指定的专家会同时执行
            - 如果有专家超时或出错，会返回error结果
            - 返回顺序不固定
        """
        timeout = timeout_sec or self.default_timeout_sec * len(expert_names)
        
        # 创建任务列表
        tasks = []
        for name in expert_names:
            expert = self.get_expert(name)
            if not expert:
                self.logger.warning(f"Expert '{name}' not found")
                continue
            
            # 每个专家单独的超时控制
            task = expert.execute(request, timeout_sec=self.default_timeout_sec)
            tasks.append(task)
        
        if not tasks:
            self.logger.warning("No valid experts to execute")
            return []
        
        # 并行执行所有任务
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=timeout
            )
            
            # 过滤出真正的ExpertResult
            valid_results = [
                r for r in results
                if isinstance(r, ExpertResult)
            ]
            
            return valid_results
            
        except asyncio.TimeoutError:
            self.logger.error(f"Parallel execution timed out after {timeout}s")
            return []
        except Exception as e:
            self.logger.error(f"Parallel execution failed: {str(e)}", exc_info=True)
            return []
    
    async def process_request(
        self,
        request: ExpertRequest,
        expert_names: Optional[List[str]] = None,
        timeout_sec: Optional[float] = None
    ) -> AggregatedResult:
        """
        处理一个请求 (完整的MOE流程)。
        
        Args:
            request: 用户请求
            expert_names: 要使用的专家列表 (None = 使用所有)
            timeout_sec: 超时时间
        
        Returns:
            AggregatedResult: 聚合后的结果
        """
        timestamp_start = datetime.now().timestamp()
        
        # 选择要执行的专家
        if expert_names is None:
            expert_names = self.get_available_experts()
        
        self.logger.info(
            f"Processing request with experts: {expert_names}"
        )
        
        # 并行执行
        results = await self.execute_experts_parallel(
            expert_names,
            request,
            timeout_sec
        )
        
        # 聚合结果
        aggregated = self._aggregate_results(results)
        
        timestamp_end = datetime.now().timestamp()
        aggregated.duration_ms = (timestamp_end - timestamp_start) * 1000
        
        self.logger.info(
            f"Request processed in {aggregated.duration_ms:.2f}ms"
        )
        
        return aggregated
    
    def _aggregate_results(self, results: List[ExpertResult]) -> AggregatedResult:
        """
        聚合多个专家的结果。
        
        简单聚合策略 (Phase 1):
        - 收集所有成功的结果
        - 计算平均置信度
        - 评估一致性
        """
        # 过滤出没有error的结果
        successful_results = [r for r in results if not r.error]
        
        if not successful_results:
            # 全部失败
            return AggregatedResult(
                final_result={"error": "All experts failed"},
                expert_results=results,
                overall_confidence=0.0,
                num_experts=len(results),
                consensus_level="none",
                duration_ms=0.0
            )
        
        # 计算平均置信度
        avg_confidence = (
            sum(r.confidence for r in successful_results) /
            len(successful_results)
        )
        
        # 评估一致性 (简单版本)
        confidence_stddev = (
            sum((r.confidence - avg_confidence) ** 2 for r in successful_results) /
            len(successful_results)
        ) ** 0.5
        
        if confidence_stddev < 0.1:
            consensus = "high"
        elif confidence_stddev < 0.2:
            consensus = "medium"
        else:
            consensus = "low"
        
        return AggregatedResult(
            final_result={
                "num_successful": len(successful_results),
                "num_failed": len(results) - len(successful_results),
                "consensus": consensus,
            },
            expert_results=results,
            overall_confidence=avg_confidence,
            num_experts=len(results),
            consensus_level=consensus,
            duration_ms=0.0
        )
```

**验收标准**:
- [ ] 可以注册和管理多个Expert
- [ ] 支持并行执行专家
- [ ] 有超时控制机制
- [ ] 结果聚合工作正常

**预计代码量**: 400行

---

## 📋 Day 5-6 (Fri-Sat 04-11 ~ 04-12) - Demo专家和完整测试 (400行代码)

### 任务 4.1: 实现3个Demo专家 (1天)

**目标**: 实现可运行的Demo专家用于测试

**文件**: 
- `src/experts/demo_expert_1.py` (100行)
- `src/experts/demo_expert_2.py` (100行)
- `src/experts/demo_expert_3.py` (100行)

**代码示例 (Demo Expert 1 - 简单返回)**:

```python
from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, ExpertResult
from datetime import datetime

class DemoExpert1(Expert):
    """
    Demo专家 1: 返回固定结果。
    
    用途: 测试基本框架
    特点: 总是返回相同的结果，很快完成
    """
    
    def __init__(self):
        super().__init__(name="DemoExpert1", version="1.0")
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """
        简单的分析 - 返回固定结果。
        """
        # 模拟一点处理时间
        import asyncio
        await asyncio.sleep(0.1)
        
        return ExpertResult(
            expert_name=self.name,
            result={
                "analysis": "This is a demo result from Expert 1",
                "message": f"Processed: {request.text[:50]}",
                "confidence_score": 0.85,
            },
            confidence=0.85,
            metadata={
                "version": self.version,
                "type": "demo",
            },
            timestamp_start=datetime.now().timestamp(),
            timestamp_end=datetime.now().timestamp(),
        )
    
    def get_supported_tasks(self) -> list:
        return ["demo", "test"]

# 类似地实现 DemoExpert2 和 DemoExpert3
```

**验收标准**:
- [ ] 3个Demo专家都能成功执行
- [ ] 返回正确的ExpertResult格式
- [ ] 没有运行时错误

**预计代码量**: 300行

---

### 任务 4.2: 编写完整的单元和集成测试 (1.5天)

**目标**: 确保框架核心功能正常工作

**文件**:
- `tests/unit/test_models.py` (100行)
- `tests/unit/test_expert_base.py` (150行)
- `tests/unit/test_moe_orchestrator.py` (150行)
- `tests/integration/test_full_pipeline.py` (150行)

**测试框架示例**:

```python
import pytest
import asyncio
from src.models.request_response import ExpertRequest, ExpertResult
from src.experts.demo_expert_1 import DemoExpert1
from src.core.moe_orchestrator import MOEOrchestrator

@pytest.mark.asyncio
async def test_demo_expert_1_execution():
    """测试Demo专家1