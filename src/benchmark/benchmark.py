"""
Benchmark Framework

Performance benchmarking tools.
"""

import time
import statistics
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass
import json


@dataclass
class BenchmarkResult:
    """Result of a benchmark"""
    name: str
    iterations: int
    times: List[float]
    
    @property
    def min_time(self) -> float:
        return min(self.times)
    
    @property
    def max_time(self) -> float:
        return max(self.times)
    
    @property
    def avg_time(self) -> float:
        return statistics.mean(self.times)
    
    @property
    def median_time(self) -> float:
        if len(self.times) % 2 == 0:
            return statistics.median(self.times)
        return statistics.median(self.times)
    
    @property
    def stddev(self) -> float:
        if len(self.times) < 2:
            return 0.0
        return statistics.stdev(self.times)
    
    @property
    def total_time(self) -> float:
        return sum(self.times)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'iterations': self.iterations,
            'min_ms': round(self.min_time * 1000, 3),
            'max_ms': round(self.max_time * 1000, 3),
            'avg_ms': round(self.avg_time * 1000, 3),
            'median_ms': round(self.median_time * 1000, 3),
            'stddev_ms': round(self.stddev * 1000, 3),
            'total_ms': round(self.total_time * 1000, 3),
        }


class Benchmark:
    """Performance benchmarking tool"""

    def __init__(self):
        """Initialize benchmark"""
        self.results: List[BenchmarkResult] = []

    def run(
        self,
        func: Callable,
        name: str,
        iterations: int = 100,
        *args: Any,
        **kwargs: Any,
    ) -> BenchmarkResult:
        """
        Run a benchmark.

        Args:
            func: Function to benchmark
            name: Benchmark name
            iterations: Number of iterations
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Benchmark result
        """
        times: List[float] = []

        for _ in range(iterations):
            start = time.time()
            func(*args, **kwargs)
            elapsed = time.time() - start
            times.append(elapsed)

        result = BenchmarkResult(name=name, iterations=iterations, times=times)
        self.results.append(result)
        return result

    async def run_async(
        self,
        func: Callable,
        name: str,
        iterations: int = 100,
        *args: Any,
        **kwargs: Any,
    ) -> BenchmarkResult:
        """
        Run an async benchmark.

        Args:
            func: Async function to benchmark
            name: Benchmark name
            iterations: Number of iterations
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Benchmark result
        """
        times: List[float] = []

        for _ in range(iterations):
            start = time.time()
            await func(*args, **kwargs)
            elapsed = time.time() - start
            times.append(elapsed)

        result = BenchmarkResult(name=name, iterations=iterations, times=times)
        self.results.append(result)
        return result

    def get_results(self) -> List[Dict[str, Any]]:
        """
        Get all benchmark results.

        Returns:
            List of benchmark results as dictionaries
        """
        return [result.to_dict() for result in self.results]

    def get_summary(self) -> Dict[str, Any]:
        """
        Get benchmark summary.

        Returns:
            Summary dictionary
        """
        if not self.results:
            return {}

        total_time = sum(r.total_time for r in self.results)
        return {
            'total_benchmarks': len(self.results),
            'total_time_ms': round(total_time * 1000, 3),
            'benchmarks': self.get_results(),
        }

    def clear(self) -> None:
        """Clear all results"""
        self.results.clear()

    def export_json(self, filepath: str) -> None:
        """
        Export results to JSON.

        Args:
            filepath: File path to export to
        """
        with open(filepath, 'w') as f:
            json.dump(self.get_summary(), f, indent=2)

    def print_results(self) -> None:
        """Print formatted benchmark results"""
        print("\n" + "=" * 70)
        print("BENCHMARK RESULTS")
        print("=" * 70)

        for result in self.results:
            data = result.to_dict()
            print(f"\n{data['name']}")
            print(f"  Iterations: {data['iterations']}")
            print(f"  Min:        {data['min_ms']:.3f}ms")
            print(f"  Max:        {data['max_ms']:.3f}ms")
            print(f"  Average:    {data['avg_ms']:.3f}ms")
            print(f"  Median:     {data['median_ms']:.3f}ms")
            print(f"  Std Dev:    {data['stddev_ms']:.3f}ms")
            print(f"  Total:      {data['total_ms']:.3f}ms")

        print("\n" + "=" * 70)
        print(f"Total Benchmarks: {len(self.results)}")
        print("=" * 70 + "\n")
