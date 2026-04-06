# SiliconSoul MOE - Development Guide

## Getting Started

### Prerequisites

- Python 3.9+
- pip or conda
- Git

### Setup Development Environment

```bash
# Clone/navigate to project
cd siliconsoul-moe

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m pytest --version
black --version
mypy --version
```

## Project Structure

```
siliconsoul-moe/
├── src/                    # Source code
│   ├── core/              # Core framework components
│   ├── experts/           # Expert implementations
│   ├── models/            # Data models (Pydantic)
│   └── utils/             # Utility functions
├── tests/                 # Test files
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── docs/                 # Documentation
├── config/               # Configuration files
├── scripts/              # Helper scripts
└── requirements.txt      # Python dependencies
```

## Writing Tests

### Unit Tests

Test individual components in isolation:

```python
# tests/unit/test_my_component.py
import pytest
from src.experts.demo_expert_1 import DemoExpert1
from src.models.request_response import ExpertRequest

class TestDemoExpert1:
    @pytest.fixture
    def expert(self):
        return DemoExpert1()
    
    @pytest.fixture
    def request(self):
        return ExpertRequest(
            text="test",
            user_id="test_user"
        )
    
    @pytest.mark.asyncio
    async def test_analyze(self, expert, request):
        result = await expert.analyze(request)
        
        assert result.expert_name == "DemoExpert1"
        assert result.confidence > 0
        assert not result.error
```

### Integration Tests

Test multiple components together:

```python
# tests/integration/test_full_pipeline.py
import pytest
from src.core.moe_orchestrator import MOEOrchestrator
from src.experts.demo_expert_1 import DemoExpert1
from src.models.request_response import ExpertRequest

@pytest.mark.asyncio
async def test_full_pipeline():
    moe = MOEOrchestrator()
    moe.register_expert(DemoExpert1())
    
    request = ExpertRequest(text="test", user_id="user1")
    result = await moe.process_request(request)
    
    assert result.overall_confidence > 0
    assert len(result.expert_results) > 0
```

### Running Tests

```bash
# All tests
python -m pytest

# With coverage
python -m pytest --cov=src --cov-report=html

# Unit tests only
python -m pytest tests/unit -m unit

# Integration tests
python -m pytest tests/integration -m integration

# Specific test
python -m pytest tests/unit/test_models.py::TestExpertRequest

# Verbose output
python -m pytest -v

# Stop on first failure
python -m pytest -x
```

## Code Quality

### Formatting

Format code with Black:

```bash
# Format all Python files
black src/ tests/

# Check formatting without changing
black --check src/
```

### Linting

Check code style with Pylint:

```bash
# Lint source
pylint src/

# Lint tests
pylint tests/

# Generate report
pylint --output-format=parseable src/ > lint-report.txt
```

### Type Checking

Validate types with mypy:

```bash
# Check types
mypy src/

# Strict mode
mypy --strict src/

# Generate report
mypy src/ > type-check-report.txt
```

### Complete Quality Check

```bash
# Run all checks
./scripts/run_tests.sh
```

## Creating a New Expert

### Step 1: Create Expert File

```bash
# Create new file
touch src/experts/my_expert.py
```

### Step 2: Implement Expert

```python
# src/experts/my_expert.py
from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, ExpertResult
from datetime import datetime
import asyncio

class MyExpert(Expert):
    """
    My Custom Expert - Short description.
    
    Longer description of what this expert does,
    how it works, and any special characteristics.
    """
    
    def __init__(self):
        super().__init__(name="MyExpert", version="1.0")
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """
        Analyze user request and return result.
        
        Args:
            request: ExpertRequest with user input
        
        Returns:
            ExpertResult with analysis result
        """
        timestamp_start = datetime.now().timestamp()
        
        try:
            # Your analysis logic here
            text = request.text
            
            # Simulate some async work
            await asyncio.sleep(0.1)
            
            # Build result
            analysis_result = {
                "input_length": len(text),
                "analysis": "your analysis here",
                "score": 0.85,
            }
            
            timestamp_end = datetime.now().timestamp()
            
            return ExpertResult(
                expert_name=self.name,
                result=analysis_result,
                confidence=0.92,
                metadata={
                    "version": self.version,
                    "model": "your_model_name",
                },
                timestamp_start=timestamp_start,
                timestamp_end=timestamp_end,
            )
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            
            timestamp_end = datetime.now().timestamp()
            return ExpertResult(
                expert_name=self.name,
                result={},
                confidence=0.0,
                timestamp_start=timestamp_start,
                timestamp_end=timestamp_end,
                error=f"Analysis error: {str(e)}",
            )
    
    def get_supported_tasks(self) -> list:
        """Return list of task types this expert handles."""
        return ["my_task", "analysis"]
```

### Step 3: Create Unit Test

```bash
touch tests/unit/test_my_expert.py
```

```python
# tests/unit/test_my_expert.py
import pytest
from src.experts.my_expert import MyExpert
from src.models.request_response import ExpertRequest

class TestMyExpert:
    @pytest.fixture
    def expert(self):
        return MyExpert()
    
    def test_initialization(self, expert):
        assert expert.name == "MyExpert"
        assert expert.version == "1.0"
    
    def test_supported_tasks(self, expert):
        tasks = expert.get_supported_tasks()
        assert "my_task" in tasks
    
    @pytest.mark.asyncio
    async def test_analyze_success(self, expert):
        request = ExpertRequest(
            text="test input",
            user_id="user123"
        )
        
        result = await expert.analyze(request)
        
        assert result.expert_name == "MyExpert"
        assert result.confidence > 0
        assert not result.error
        assert result.result.get("analysis") is not None
    
    @pytest.mark.asyncio
    async def test_metadata(self, expert):
        metadata = expert.get_metadata()
        
        assert "name" in metadata
        assert "version" in metadata
        assert "supported_tasks" in metadata
```

### Step 4: Integration Test

Add test to `tests/integration/test_full_pipeline.py`:

```python
@pytest.mark.asyncio
async def test_with_my_expert():
    moe = MOEOrchestrator()
    moe.register_expert(MyExpert())
    
    request = ExpertRequest(text="test", user_id="user1")
    result = await moe.process_request(request)
    
    assert len(result.expert_results) > 0
    assert any(r.expert_name == "MyExpert" for r in result.expert_results)
```

### Step 5: Run Tests

```bash
# Test your expert
python -m pytest tests/unit/test_my_expert.py -v

# Run with coverage
python -m pytest tests/unit/test_my_expert.py --cov=src.experts.my_expert

# Integration test
python -m pytest tests/integration/ -v
```

## Debugging

### Enable Debug Logging

```python
import logging

# Set logging level
logging.basicConfig(level=logging.DEBUG)

# Get logger for specific module
logger = logging.getLogger("src.core.moe_orchestrator")
logger.setLevel(logging.DEBUG)
```

### Debug a Test

```bash
# Run single test with debugging
python -m pytest tests/unit/test_my_expert.py::TestMyExpert::test_analyze_success -vvv

# Run with pdb breakpoint
python -m pytest tests/unit/test_my_expert.py -s --pdb
```

### Print Debug Info

```python
# In your expert
result = await expert.analyze(request)
print(f"Debug: {result.result}")  # Will print during -s flag
```

## Performance Profiling

### Measure Execution Time

```python
import time

async def profile_expert():
    expert = MyExpert()
    request = ExpertRequest(text="test", user_id="user1")
    
    start = time.time()
    result = await expert.execute(request)
    elapsed = time.time() - start
    
    print(f"Execution time: {elapsed*1000:.2f}ms")
    print(f"Reported duration: {result.duration_ms:.2f}ms")
```

### Memory Profiling

```bash
# Install memory_profiler
pip install memory-profiler

# Profile your function
python -m memory_profiler profile_script.py
```

## Common Issues

### Issue: Tests timeout

**Solution**: Check if your expert has infinite loops or blocking I/O

```python
# Bad: Blocking I/O
import time
time.sleep(5)  # Will timeout

# Good: Async I/O
await asyncio.sleep(5)
```

### Issue: Pydantic validation errors

**Solution**: Ensure all required fields are provided

```python
# Bad
request = ExpertRequest(text="test")  # Missing user_id

# Good
request = ExpertRequest(text="test", user_id="user1")
```

### Issue: Import errors

**Solution**: Ensure __init__.py files exist and imports are correct

```bash
# Check structure
ls -la src/
ls -la src/experts/
# Should show __init__.py in each directory
```

## Version Control

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-expert

# Make changes and commit
git add src/experts/my_expert.py
git commit -m "Add MyExpert implementation"

# Push and create PR
git push origin feature/my-expert
```

### Commit Message Format

```
[Type] Brief description

- Detailed change 1
- Detailed change 2

Fixes #123
```

Types: `[Feature]`, `[Bugfix]`, `[Docs]`, `[Test]`, `[Refactor]`

## Continuous Integration

### Pre-commit Checks

```bash
# Format
black src/

# Type check
mypy src/

# Lint
pylint src/

# Test
python -m pytest

# Only then commit
git commit ...
```

## Deployment

### Building Distribution

```bash
# Build source distribution
python setup.py sdist

# Build wheel
python setup.py bdist_wheel
```

### Installing from Local

```bash
# Install in development mode
pip install -e .
```

## Resources

- [Python asyncio docs](https://docs.python.org/3/library/asyncio.html)
- [Pydantic docs](https://docs.pydantic.dev/)
- [Pytest docs](https://docs.pytest.org/)
- [Black docs](https://black.readthedocs.io/)

---

**Last Updated**: 2026-04-07
