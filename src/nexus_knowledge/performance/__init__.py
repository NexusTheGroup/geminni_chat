"""Performance utilities and benchmarks for NexusKnowledge."""

default_benchmark_thresholds = {
    "ingestion_ms": 100.0,
    "normalization_ms": 150.0,
    "search_ms": 75.0,
}

__all__ = ["default_benchmark_thresholds"]
