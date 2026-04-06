"""
Unit tests for monitoring system
"""

import pytest
import time
from src.monitoring.metrics_collector import MetricsCollector, MetricStats
from src.monitoring.monitor import SystemMonitor


class TestMetricsCollector:
    """Tests for metrics collector"""

    def test_record_metric(self):
        """Test recording a metric"""
        collector = MetricsCollector()
        collector.record('latency', 100.5)

        assert 'latency' in collector.metrics
        assert len(collector.metrics['latency']) == 1
        assert collector.metrics['latency'][0].value == 100.5

    def test_metric_stats(self):
        """Test metric statistics"""
        collector = MetricsCollector()
        for i in range(10):
            collector.record('values', i * 10)

        stats = collector.get_metric('values')
        assert stats['count'] == 10
        assert stats['average'] == 45.0
        assert stats['min'] == 0.0
        assert stats['max'] == 90.0

    def test_get_recent_metrics(self):
        """Test getting recent metrics"""
        collector = MetricsCollector()
        collector.record('test', 100)
        time.sleep(0.1)
        collector.record('test', 200)

        recent = collector.get_recent('test', duration=1.0)
        assert len(recent) == 2

    def test_clear_metrics(self):
        """Test clearing metrics"""
        collector = MetricsCollector()
        collector.record('test', 100)
        assert len(collector.metrics['test']) > 0

        collector.clear()
        assert len(collector.metrics) == 0
        assert len(collector.stats) == 0


class TestSystemMonitor:
    """Tests for system monitor"""

    def test_record_request(self):
        """Test recording requests"""
        monitor = SystemMonitor()
        monitor.record_request(100.0, success=True)
        monitor.record_request(150.0, success=False)

        assert monitor.request_count == 2
        assert monitor.success_count == 1
        assert monitor.error_count == 1

    def test_get_status(self):
        """Test getting status"""
        monitor = SystemMonitor()
        monitor.record_request(100.0, success=True)
        monitor.record_request(100.0, success=True)

        status = monitor.get_status()
        assert status['total_requests'] == 2
        assert status['success_count'] == 2
        assert status['error_count'] == 0
        assert status['success_rate'] == 100.0

    def test_success_rate_calculation(self):
        """Test success rate calculation"""
        monitor = SystemMonitor()
        for _ in range(95):
            monitor.record_request(100.0, success=True)
        for _ in range(5):
            monitor.record_request(100.0, success=False)

        status = monitor.get_status()
        assert status['success_rate'] == pytest.approx(95.0, abs=0.1)

    def test_get_health(self):
        """Test getting health status"""
        monitor = SystemMonitor()
        
        # Healthy
        for _ in range(100):
            monitor.record_request(100.0, success=True)
        health = monitor.get_health()
        assert health['health'] == 'healthy'

        # Degraded
        monitor.reset()
        for _ in range(96):
            monitor.record_request(100.0, success=True)
        for _ in range(4):
            monitor.record_request(100.0, success=False)
        health = monitor.get_health()
        assert health['health'] == 'degraded'

    def test_get_metrics(self):
        """Test getting all metrics"""
        monitor = SystemMonitor()
        monitor.record_request(100.0)
        monitor.record_request(200.0)

        metrics = monitor.get_metrics()
        assert 'status' in metrics
        assert 'metrics' in metrics
        assert metrics['status']['total_requests'] == 2

    def test_reset_monitor(self):
        """Test resetting monitor"""
        monitor = SystemMonitor()
        monitor.record_request(100.0)
        assert monitor.request_count == 1

        monitor.reset()
        assert monitor.request_count == 0
        assert monitor.error_count == 0
        assert monitor.success_count == 0


class TestMetricStats:
    """Tests for metric stats"""

    def test_add_values(self):
        """Test adding values to stats"""
        stats = MetricStats(name='test')
        stats.add_value(10)
        stats.add_value(20)
        stats.add_value(30)

        assert stats.count == 3
        assert stats.sum == 60
        assert stats.min == 10
        assert stats.max == 30
        assert stats.average == 20

    def test_median(self):
        """Test median calculation"""
        stats = MetricStats(name='test')
        for v in [1, 2, 3, 4, 5]:
            stats.add_value(v)

        assert stats.median == 3

    def test_stddev(self):
        """Test standard deviation"""
        stats = MetricStats(name='test')
        for v in [1, 2, 3, 4, 5]:
            stats.add_value(v)

        assert stats.stddev > 0

    def test_to_dict(self):
        """Test converting to dictionary"""
        stats = MetricStats(name='test')
        stats.add_value(10)
        stats.add_value(20)

        result = stats.to_dict()
        assert result['name'] == 'test'
        assert result['count'] == 2
        assert result['average'] == 15
