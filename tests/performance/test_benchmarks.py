from __future__ import annotations

from nexus_knowledge.performance.benchmarks import run_single_user_benchmark


def test_single_user_benchmark_runs(sqlite_db) -> None:
    _, session_factory, _ = sqlite_db

    report = run_single_user_benchmark(session_factory, iterations=2)
    assert {"ingestion_ms", "normalization_ms", "search_ms"}.issubset(report.keys())

    for result in report.values():
        assert result.iterations == 2
        assert result.average_ms >= 0
        assert result.max_ms >= 0
        assert isinstance(result.passed, bool)
