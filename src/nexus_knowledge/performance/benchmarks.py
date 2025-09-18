"""Utility routines for measuring single-user performance baselines."""

from __future__ import annotations

import statistics
import time
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from nexus_knowledge.analysis.pipeline import run_analysis_for_raw_data
from nexus_knowledge.ingestion import ingest_raw_payload
from nexus_knowledge.ingestion.service import normalize_raw_data
from nexus_knowledge.performance import default_benchmark_thresholds
from nexus_knowledge.search import hybrid_search
from sqlalchemy.orm import Session, sessionmaker


@dataclass
class BenchmarkResult:
    """Aggregate metrics for a benchmarked operation."""

    name: str
    samples_ms: list[float]
    threshold_ms: float

    @property
    def iterations(self) -> int:
        return len(self.samples_ms)

    @property
    def average_ms(self) -> float:
        return statistics.mean(self.samples_ms) if self.samples_ms else 0.0

    @property
    def max_ms(self) -> float:
        return max(self.samples_ms) if self.samples_ms else 0.0

    @property
    def passed(self) -> bool:
        return self.average_ms <= self.threshold_ms


def _sample_payload(iteration: int) -> dict[str, object]:
    message_template = {
        "role": "user" if iteration % 2 == 0 else "assistant",
        "content": f"Benchmark message {iteration}",
        "timestamp": f"2025-01-01T00:00:{iteration:02d}Z",
    }
    return {
        "source_platform": "benchmark",
        "source_id": f"benchmark-{iteration}",
        "messages": [
            message_template,
            {
                "role": "assistant" if iteration % 2 == 0 else "user",
                "content": f"Response to benchmark message {iteration}",
                "timestamp": f"2025-01-01T00:00:{(iteration + 1):02d}Z",
            },
        ],
    }


def _time_call(func: Callable[[], object]) -> float:
    start = time.perf_counter()
    func()
    return (time.perf_counter() - start) * 1000


def run_single_user_benchmark(
    session_factory: sessionmaker[Session],
    *,
    iterations: int = 5,
    thresholds: Mapping[str, float] | None = None,
    include_analysis: bool = False,
    mlflow_uri_factory: Callable[[], str | None] | None = None,
) -> dict[str, BenchmarkResult]:
    """Execute a lightweight ingestion/normalization/search benchmark."""
    results: dict[str, list[float]] = {
        "ingestion_ms": [],
        "normalization_ms": [],
        "search_ms": [],
    }
    if include_analysis:
        results["analysis_ms"] = []

    for i in range(iterations):
        payload = _sample_payload(i)

        with session_factory.begin() as session:
            start = time.perf_counter()
            raw_data_id = ingest_raw_payload(
                session,
                source_type="benchmark",
                content=payload,
                metadata={"source_platform": "benchmark"},
                source_id=(
                    payload.get("source_id") if isinstance(payload, dict) else None
                ),
            )
            duration = (time.perf_counter() - start) * 1000
            results["ingestion_ms"].append(duration)

        with session_factory.begin() as session:
            duration = _time_call(lambda: normalize_raw_data(session, raw_data_id))
            results["normalization_ms"].append(duration)

        if include_analysis:
            if mlflow_uri_factory is not None:
                uri = mlflow_uri_factory()
                if uri:
                    import os

                    os.environ.setdefault("MLFLOW_TRACKING_URI", uri)

            with session_factory.begin() as session:
                duration = _time_call(
                    lambda: run_analysis_for_raw_data(session, raw_data_id),
                )
                results["analysis_ms"].append(duration)

        with session_factory.begin() as session:
            duration = _time_call(
                lambda: hybrid_search(session, "benchmark message", limit=5),
            )
            results["search_ms"].append(duration)

    threshold_lookup = dict(default_benchmark_thresholds)
    if thresholds:
        threshold_lookup.update(thresholds)

    report: dict[str, BenchmarkResult] = {}
    for name, samples in results.items():
        report[name] = BenchmarkResult(
            name=name,
            samples_ms=samples,
            threshold_ms=threshold_lookup.get(name, float("inf")),
        )
    return report


def format_report(results: Iterable[BenchmarkResult]) -> str:
    """Pretty-print benchmark results for CLI usage."""
    lines = ["Benchmark Report"]
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        lines.append(
            f"- {result.name}: avg={result.average_ms:.2f}ms "
            f"(max={result.max_ms:.2f}ms, n={result.iterations}) <= {result.threshold_ms:.2f}ms [{status}]",
        )
    return "\n".join(lines)


if __name__ == "__main__":
    from nexus_knowledge.db.session import get_session_factory

    session_factory = get_session_factory()
    report = run_single_user_benchmark(session_factory)
    print(format_report(report.values()))
