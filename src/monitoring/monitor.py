"""
System Monitor

Monitors system health and performance metrics.
"""

import time
from typing import Dict, Optional
from datetime import datetime, timedelta
from src.monitoring.metrics_collector import MetricsCollector


class SystemMonitor:
    """Monitors system health and performance"""

    def __init__(self):
        """Initialize system monitor"""
        self.collector = MetricsCollector()
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.success_count = 0
        self.total_latency = 0.0

    def record_request(self, duration_ms: float, success: bool = True) -> None:
        """
        Record a request.

        Args:
            duration_ms: Request duration in milliseconds
            success: Whether the request was successful
        """
        self.request_count += 1
        self.total_latency += duration_ms

        if success:
            self.success_count += 1
        else:
            self.error_count += 1

        # Record metrics
        self.collector.record('request_duration_ms', duration_ms)
        self.collector.record('request_count', self.request_count)
        self.collector.record('error_count', self.error_count)

    def get_status(self) -> Dict:
        """
        Get system status.

        Returns:
            System status dictionary
        """
        uptime_seconds = time.time() - self.start_time
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        uptime_days = int(uptime_seconds // 86400)

        uptime_str = f"{uptime_days}d {uptime_hours}h"

        success_rate = (
            (self.success_count / self.request_count * 100)
            if self.request_count > 0
            else 0.0
        )

        avg_latency = (
            (self.total_latency / self.request_count)
            if self.request_count > 0
            else 0.0
        )

        return {
            'uptime': uptime_str,
            'uptime_seconds': uptime_seconds,
            'total_requests': self.request_count,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'success_rate': success_rate,
            'error_rate': 100.0 - success_rate,
            'avg_latency_ms': avg_latency,
            'timestamp': datetime.now().isoformat(),
        }

    def get_metrics(self) -> Dict:
        """
        Get detailed metrics.

        Returns:
            Detailed metrics dictionary
        """
        return {
            'status': self.get_status(),
            'metrics': self.collector.get_all_metrics(),
        }

    def get_recent_latencies(self, duration: float = 60.0) -> Dict:
        """
        Get recent latency data.

        Args:
            duration: Duration in seconds

        Returns:
            Recent latency data
        """
        recent_points = self.collector.get_recent('request_duration_ms', duration)
        return {
            'points': [
                {
                    'timestamp': p.timestamp,
                    'value': p.value,
                }
                for p in recent_points
            ],
            'count': len(recent_points),
        }

    def get_health(self) -> Dict:
        """
        Get system health.

        Returns:
            Health status dictionary
        """
        status = self.get_status()
        success_rate = status['success_rate']

        if success_rate >= 99.0:
            health = 'healthy'
        elif success_rate >= 95.0:
            health = 'degraded'
        else:
            health = 'unhealthy'

        return {
            'health': health,
            'success_rate': success_rate,
            'avg_latency_ms': status['avg_latency_ms'],
        }

    def reset(self) -> None:
        """Reset all metrics"""
        self.request_count = 0
        self.error_count = 0
        self.success_count = 0
        self.total_latency = 0.0
        self.collector.clear()
        self.start_time = time.time()
