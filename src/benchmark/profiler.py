"""
Profiler

Performance profiling and analysis.
"""

import cProfile
import pstats
import io
from typing import Callable, Dict, Any, Optional
from contextlib import contextmanager
import time


class Profiler:
    """Performance profiler"""

    def __init__(self):
        """Initialize profiler"""
        self.profiler = cProfile.Profile()
        self.stats: Optional[pstats.Stats] = None

    @contextmanager
    def profile(self):
        """Context manager for profiling"""
        self.profiler.enable()
        try:
            yield
        finally:
            self.profiler.disable()

    def profile_function(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """
        Profile a function call.

        Args:
            func: Function to profile
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function return value
        """
        with self.profile():
            return func(*args, **kwargs)

    def get_stats(self) -> str:
        """
        Get profiling statistics.

        Returns:
            Formatted statistics string
        """
        s = io.StringIO()
        ps = pstats.Stats(self.profiler, stream=s)
        ps.strip_dirs()
        ps.sort_stats('cumulative')
        ps.print_stats(10)  # Top 10 functions
        return s.getvalue()

    def print_stats(self) -> None:
        """Print profiling statistics"""
        print(self.get_stats())

    def reset(self) -> None:
        """Reset profiler"""
        self.profiler = cProfile.Profile()
        self.stats = None


class SimpleTimer:
    """Simple timer for measuring execution time"""

    def __init__(self):
        """Initialize timer"""
        self.times: Dict[str, list] = {}

    @contextmanager
    def time(self, label: str):
        """
        Time a block of code.

        Args:
            label: Label for the timing
        """
        if label not in self.times:
            self.times[label] = []

        start = time.time()
        try:
            yield
        finally:
            elapsed = time.time() - start
            self.times[label].append(elapsed)

    def get_average(self, label: str) -> float:
        """
        Get average time for a label.

        Args:
            label: Label name

        Returns:
            Average time in seconds
        """
        if label not in self.times or not self.times[label]:
            return 0.0
        times = self.times[label]
        return sum(times) / len(times)

    def get_total(self, label: str) -> float:
        """
        Get total time for a label.

        Args:
            label: Label name

        Returns:
            Total time in seconds
        """
        if label not in self.times:
            return 0.0
        return sum(self.times[label])

    def get_count(self, label: str) -> int:
        """
        Get count for a label.

        Args:
            label: Label name

        Returns:
            Number of times recorded
        """
        if label not in self.times:
            return 0
        return len(self.times[label])

    def get_summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Get timing summary.

        Returns:
            Summary dictionary
        """
        result = {}
        for label, times in self.times.items():
            if not times:
                continue
            result[label] = {
                'count': len(times),
                'total_ms': round(sum(times) * 1000, 3),
                'avg_ms': round((sum(times) / len(times)) * 1000, 3),
                'min_ms': round(min(times) * 1000, 3),
                'max_ms': round(max(times) * 1000, 3),
            }
        return result

    def print_summary(self) -> None:
        """Print timing summary"""
        summary = self.get_summary()
        print("\n" + "=" * 60)
        print("TIMING SUMMARY")
        print("=" * 60)
        for label, stats in summary.items():
            print(f"\n{label}:")
            print(f"  Count:   {stats['count']}")
            print(f"  Total:   {stats['total_ms']:.3f}ms")
            print(f"  Average: {stats['avg_ms']:.3f}ms")
            print(f"  Min:     {stats['min_ms']:.3f}ms")
            print(f"  Max:     {stats['max_ms']:.3f}ms")
        print("\n" + "=" * 60 + "\n")

    def reset(self) -> None:
        """Reset all timings"""
        self.times.clear()
