"""Benchmark tests for fromager resolver functionality."""

import pytest
from pytest_codspeed import BenchmarkFixture


@pytest.mark.benchmark
def test_simple_operation(benchmark: BenchmarkFixture) -> None:
    """Benchmark a simple operation."""

    def simple_computation():
        # Simple computation for testing
        total = 0
        for i in range(1000):
            total += i
        return total

    result = benchmark(simple_computation)
    assert result == sum(range(1000))
