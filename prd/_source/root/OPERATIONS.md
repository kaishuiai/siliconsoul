# SiliconSoul Operations Manual

Day-to-day operations guide for SiliconSoul.

## Daily Operations

### Morning Checklist

```bash
# 1. Check service status
./scripts/deploy.sh status

# 2. Review logs for errors
tail -100 logs/siliconsoul.log | grep ERROR

# 3. Check system health
curl -s http://localhost:8000/api/health | jq

# 4. Monitor metrics
curl -s http://localhost:8000/api/monitor/metrics | jq

# 5. Check disk space
df -h /data /logs
```

### Performance Monitoring

```bash
# Real-time monitoring
watch -n 5 'curl -s http://localhost:8000/api/monitor/metrics'

# Cache performance
curl http://localhost:8000/api/cache/stats

# Expert statistics
curl http://localhost:8000/api/experts | jq

# Node status
curl http://localhost:8000/api/monitor/nodes
```

## Common Tasks

### Start Service

```bash
# Using deployment script
./scripts/deploy.sh start

# Or Docker
docker-compose up -d

# Verify startup
sleep 5
curl http://localhost:8000/api/health
```

### Stop Service

```bash
# Using deployment script
./scripts/deploy.sh stop

# Or Docker
docker-compose down

# Force stop
pkill -f siliconsoul
```

### Restart Service

```bash
# Graceful restart
./scripts/deploy.sh restart

# Or Docker
docker-compose restart siliconsoul
```

### View Logs

```bash
# Real-time logs
tail -f logs/siliconsoul.log

# Last 100 errors
grep ERROR logs/siliconsoul.log | tail -100

# Search logs
grep "pattern" logs/siliconsoul.log

# Log rotation
logrotate -f /etc/logrotate.d/siliconsoul
```

### Database Maintenance

```bash
# Backup database
./scripts/deploy.sh backup

# Optimize database
python -m src.cli.main storage optimize

# Clear old data
python -m src.cli.main storage cleanup --days=30

# Export data
python -m src.cli.main storage export --format=csv
```

## Troubleshooting

### Service Not Responding

```bash
# Check if running
ps aux | grep siliconsoul

# Check port
lsof -i :8000

# Restart service
./scripts/deploy.sh restart

# Check logs
tail -50 logs/siliconsoul.log
```

### High Memory Usage

```bash
# Check memory
ps -o pid,vsz,rss -p $(pgrep -f siliconsoul)

# Clear cache
curl -X POST http://localhost:8000/api/cache/clear

# Reduce cache size
python -m src.cli.main config set cache.max_size 50000

# Restart
./scripts/deploy.sh restart
```

### High Latency

```bash
# Check metrics
curl http://localhost:8000/api/monitor/metrics

# Profile experts
python scripts/benchmark.py

# Check cache hit rate
curl http://localhost:8000/api/cache/stats

# Monitor nodes
curl http://localhost:8000/api/monitor/load-balance
```

### Database Issues

```bash
# Check database
sqlite3 data/store.db ".tables"

# Repair database
python -m src.cli.main storage repair

# Backup and restore
./scripts/deploy.sh backup
python -m src.cli.main storage restore

# Reset
python -m src.cli.main storage clear
```

## Alerts & Response

### Alert Types

```
CRITICAL: Service down, data loss risk
ERROR:    Feature broken, degraded service
WARNING:  Performance issues, may affect users
INFO:     Normal operations
```

### Response Procedures

#### Service Down (CRITICAL)

1. Check logs: `tail -f logs/siliconsoul.log`
2. Verify port: `lsof -i :8000`
3. Restart: `./scripts/deploy.sh restart`
4. Health check: `curl http://localhost:8000/api/health`
5. Page oncall if not resolved

#### High Error Rate (ERROR)

1. Check specific errors: `grep ERROR logs/siliconsoul.log`
2. Review recent changes: `git log --oneline -10`
3. Rollback if needed: `git revert <commit>`
4. Restart service
5. Monitor: `watch -n 5 'curl http://localhost:8000/api/monitor/metrics'`

#### High Latency (WARNING)

1. Check metrics: `curl http://localhost:8000/api/monitor/metrics`
2. Profile: `python scripts/benchmark.py`
3. Clear cache: `curl -X POST http://localhost:8000/api/cache/clear`
4. Check load: `curl http://localhost:8000/api/monitor/load-balance`
5. Scale horizontally if needed

## Maintenance Schedule

### Daily
- ✅ Monitor metrics
- ✅ Review error logs
- ✅ Check disk space

### Weekly
- ✅ Full database backup
- ✅ Review performance trends
- ✅ Update dependencies
- ✅ Run security scan

### Monthly
- ✅ Capacity planning
- ✅ Performance optimization
- ✅ Documentation update
- ✅ Disaster recovery drill

### Quarterly
- ✅ Major version updates
- ✅ Architecture review
- ✅ Security audit
- ✅ Load testing

## Backups & Recovery

### Backup Strategy

```bash
# Automated daily backup
0 2 * * * /app/scripts/backup.sh

# Backup locations
/backups/daily/
/backups/weekly/
/backups/monthly/
```

### Restore Procedure

```bash
# List available backups
ls -la /backups/daily/

# Restore from backup
python -m src.cli.main storage restore \
  --backup=/backups/daily/backup-2026-04-06.tar.gz

# Verify restoration
curl http://localhost:8000/api/health
```

## Capacity Planning

### Current Usage

```
Data Size: ~500MB
Memory: ~1.2GB
CPU: 2 cores
Disk: 100GB available
```

### Growth Projection

```
Month    Storage    Memory    CPU
──────────────────────────────────
Today    500MB      1.2GB     2 cores
3 months 1.5GB      2.4GB     4 cores
6 months 3GB        4GB       8 cores
1 year   6GB        8GB       16 cores
```

### Scaling Plan

```
Current: Single machine
↓
Q2 2026: Dual node cluster
↓
Q3 2026: Multi-region deployment
↓
Q4 2026: Full distributed system
```

## Documentation

### Important Files

```
Operations:    OPERATIONS.md (this file)
Deployment:    DEPLOYMENT.md
Performance:   PERFORMANCE.md
Architecture:  docs/architecture.md
API:           docs/api.md
```

### Update Procedures

```bash
# Update documentation
git pull origin main

# Update to latest release
git checkout v1.7.0

# Update dependencies
pip install -r requirements.txt --upgrade

# Run tests before production
pytest tests/ -q

# Deploy updates
./scripts/deploy.sh deploy
```

## Emergency Contacts

```
On-Call Engineer: [contact info]
Team Lead: [contact info]
Slack: #siliconsoul-ops
PagerDuty: [service-key]
```

## Quick Commands Reference

```bash
# Status
./scripts/deploy.sh status

# Logs
tail -f logs/siliconsoul.log

# Health
curl http://localhost:8000/api/health

# Metrics
curl http://localhost:8000/api/monitor/metrics

# Cache Stats
curl http://localhost:8000/api/cache/stats

# Experts
curl http://localhost:8000/api/experts

# Clear Cache
curl -X POST http://localhost:8000/api/cache/clear

# Restart
./scripts/deploy.sh restart

# Backup
./scripts/deploy.sh backup
```

---

**Last Updated**: 2026-04-06  
**Version**: 1.7.0  
**Document Version**: 1.0
