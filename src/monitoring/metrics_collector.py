"""
Metrics Collector

Collects and tracks system metrics in real-time.
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import statistics


@dataclass
class MetricPoint:
    """A single metric data point"""
    timestamp: float
    value: float
    name: str


@dataclass
class MetricStats:
    """Statistics for a metric"""
    name: str
    count: int = 0
    sum: float = 0.0
    min: float = float('inf')
    max: float = float('-inf')
    values: List[float] = field(default_factory=list)

    def add_value(self, value: float) -> None:
        """Add a value to the metric"""
        self.count += 1
        self.sum += value
        self.min = min(self.min, value)
        self.max = max(self.max, value)
        self.values.append(value)

    @property
    def average(self) -> float:
        """Get average value"""
        return self.sum / self.count if self.count > 0 else 0.0

    @property
    def median(self) -> float:
        """Get median value"""
        if not self.values:
            return 0.0
        return statistics.median(self.values)

    @property
    def stddev(self) -> float:
        """Get standard deviation"""
        if len(self.values) < 2:
            return 0.0
        return statistics.stdev(self.values)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'count': self.count,
            'average': self.average,
            'min': self.min if self.min != float('inf') else 0,
            'max': self.max if self.max != float('-inf') else 0,
            'median': self.median,
            'stddev': self.stddev,
        }


class MetricsCollector:
    """Collects and tracks system metrics"""

    def __init__(self, max_points: int = 10000):
        """
        Initialize metrics collector.

        Args:
            max_points: Maximum number of metric points to keep
        """
        self.max_points = max_points
        self.metrics: Dict[str, List[MetricPoint]] = {}
        self.stats: Dict[str, MetricStats] = {}
        self.start_time = time.time()

    def record(self, name: str, value: float) -> None:
        """
        Record a metric value.

        Args:
            name: Metric name
            value: Metric value
        """
        timestamp = time.time()

        # Initialize if needed
        if name not in self.metrics:
            self.metrics[name] = []
            self.stats[name] = MetricStats(name=name)

        # Add metric point
        point = MetricPoint(timestamp=timestamp, value=value, name=name)
        self.metrics[name].append(point)

        # Update stats
        self.stats[name].add_value(value)

        # Trim old points
        if len(self.metrics[name]) > self.max_points:
            self.metrics[name] = self.metrics[name][-self.max_points:]

    def get_metric(self, name: str) -> Optional[Dict]:
        """
        Get metric statistics.

        Args:
            name: Metric name

        Returns:
            Metric statistics or None
        """
        if name not in self.stats:
            return None
        return self.stats[name].to_dict()

    def get_all_metrics(self) -> Dict[str, Dict]:
        """
        Get all metric statistics.

        Returns:
            Dictionary of all metric statistics
        """
        return {name: stat.to_dict() for name, stat in self.stats.items()}

    def get_recent(self, name: str, duration: float = 60.0) -> List[MetricPoint]:
        """
        Get recent metric points.

        Args:
            name: Metric name
            duration: Duration in seconds

        Returns:
            List of recent metric points
        """
        if name not in self.metrics:
            return []

        cutoff_time = time.time() - duration
        return [p for p in self.metrics[name] if p.timestamp >= cutoff_time]

    def clear(self) -> None:
        """Clear all metrics"""
        self.metrics.clear()
        self.stats.clear()
        self.start_time = time.time()

    def get_uptime(self) -> float:
        """Get uptime in seconds"""
        return time.time() - self.start_time

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'metrics': self.get_all_metrics(),
            'uptime': self.get_uptime(),
            'timestamp': datetime.now().isoformat(),
        }
