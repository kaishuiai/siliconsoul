# SiliconSoul Deployment Guide

Complete deployment guide for SiliconSoul MOE system.

## Prerequisites

- Python 3.9+
- pip 21+
- Docker (optional)
- Docker Compose (optional)

## Local Deployment

### 1. Clone Repository

```bash
git clone https://github.com/kaishuiai/siliconsoul.git
cd siliconsoul
```

### 2. Setup Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src
```

### 4. Configure System

```bash
# Copy default configuration
cp config/default.yaml.example config/default.yaml

# Edit configuration as needed
nano config/default.yaml
```

### 5. Start Service

```bash
# Using deployment script
bash scripts/deploy.sh deploy

# Or manually
python -m src.cli.main
```

### 6. Verify Deployment

```bash
# Check health
curl http://localhost:8000/api/health

# List experts
curl http://localhost:8000/api/experts

# Check metrics
curl http://localhost:8000/api/monitor/metrics
```

## Docker Deployment

### 1. Build Image

```bash
docker build -t siliconsoul:1.7.0 .
```

### 2. Run Container

```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --name siliconsoul \
  siliconsoul:1.7.0
```

### 3. Check Logs

```bash
docker logs -f siliconsoul
```

## Docker Compose Deployment

### 1. Start Services

```bash
docker-compose up -d
```

### 2. Check Status

```bash
docker-compose ps
```

### 3. View Logs

```bash
docker-compose logs -f siliconsoul
```

### 4. Stop Services

```bash
docker-compose down
```

## Configuration

### Environment Variables

```bash
# Logging
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR, CRITICAL

# API Gateway
API_HOST=0.0.0.0
API_PORT=8000

# Storage
STORAGE_TYPE=sqlite         # memory, json, sqlite
STORAGE_PATH=data/store.db

# Cache
CACHE_SIZE=10000
CACHE_TTL=3600

# Monitoring
ENABLE_MONITORING=true
METRICS_INTERVAL=60
```

### Configuration File

Edit `config/default.yaml`:

```yaml
system:
  name: SiliconSoul
  version: 1.7.0
  
api:
  host: 0.0.0.0
  port: 8000
  
cache:
  max_size: 10000
  ttl: 3600
  
storage:
  type: sqlite
  path: data/store.db
  
monitoring:
  enabled: true
  interval: 60
```

## Distributed Deployment

### 1. Node Registration

```bash
# Register node 1
python -m src.cli.main node register \
  --host localhost \
  --port 9000 \
  --capabilities expert1,expert2

# Register node 2
python -m src.cli.main node register \
  --host localhost \
  --port 9001 \
  --capabilities expert3,expert4
```

### 2. Configure Coordinator

```bash
# Set coordinator
python -m src.cli.main coordinator config \
  --nodes localhost:9000,localhost:9001
```

### 3. Monitor Distributed System

```bash
# Check node status
curl http://localhost:8000/api/monitor/nodes

# Get load balancing info
curl http://localhost:8000/api/monitor/load-balance
```

## Performance Optimization

### 1. Caching

Enable and configure caching:

```python
from src.cache.cache_manager import CacheManager

cache = CacheManager(max_size=10000, ttl=3600)
```

### 2. Database Optimization

Use SQLite for persistent storage:

```python
from src.storage.storage_manager import StorageManager

storage = StorageManager(
    storage_type="sqlite",
    connection_string="data/store.db"
)
```

### 3. Parallel Execution

Enable parallel expert execution:

```python
orchestrator = MOEOrchestrator()
results = orchestrator.process_parallel(text, task_type)
```

### 4. Load Balancing

Distribute work across nodes:

```python
coordinator = Coordinator(node_manager)
await coordinator.distribute_task(task_id, task)
```

## Monitoring

### 1. System Metrics

```bash
# Get metrics
curl http://localhost:8000/api/monitor/metrics

# Response:
# {
#   "uptime": "2d 3h",
#   "total_requests": 5432,
#   "success_rate": 99.8,
#   "avg_latency_ms": 234.5
# }
```

### 2. Expert Performance

```bash
# Get expert stats
curl http://localhost:8000/api/experts

# Monitor specific expert
curl http://localhost:8000/api/experts/StockAnalysisExpert
```

### 3. Alerts

Configure alerts in `config/alerts.yaml`:

```yaml
alerts:
  - name: high_latency
    condition: "avg_latency > 1000"
    action: email
    
  - name: high_error_rate
    condition: "error_rate > 1"
    action: email
```

## Maintenance

### 1. Backup

```bash
# Backup data
tar -czf backup-$(date +%Y%m%d).tar.gz data/ config/
```

### 2. Cleanup

```bash
# Clean old logs
find logs -mtime +7 -delete

# Clear cache
curl -X POST http://localhost:8000/api/cache/clear
```

### 3. Updates

```bash
# Pull latest
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
bash scripts/deploy.sh restart
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
tail -f logs/siliconsoul.log

# Verify port availability
lsof -i :8000

# Run with debug logging
LOG_LEVEL=DEBUG python -m src.cli.main
```

### High Latency

```bash
# Check metrics
curl http://localhost:8000/api/monitor/metrics

# Profile performance
python scripts/benchmark.py

# Check cache hit rate
curl http://localhost:8000/api/cache/stats
```

### Memory Issues

```bash
# Check memory usage
ps aux | grep siliconsoul

# Reduce cache size in config
# Or enable memory-mapped storage
```

## Support

- GitHub: https://github.com/kaishuiai/siliconsoul
- Issues: https://github.com/kaishuiai/siliconsoul/issues
- Documentation: https://docs.siliconsoul.ai

---

**Version**: 1.7.0  
**Last Updated**: 2026-04-06
