#!/usr/bin/env python3
"""CLI to execute the single-user performance benchmark."""

from __future__ import annotations

import argparse
from pathlib import Path

from nexus_knowledge.db.session import get_session_factory
from nexus_knowledge.performance.benchmarks import (
    format_report,
    run_single_user_benchmark,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--iterations",
        type=int,
        default=5,
        help="Number of pipeline iterations to execute (default: 5)",
    )
    parser.add_argument(
        "--include-analysis",
        action="store_true",
        help="Include sentiment analysis stage in the benchmark (requires MLflow setup)",
    )
    parser.add_argument(
        "--mlflow-dir",
        type=Path,
        default=None,
        help="Optional directory to use for MLflow tracking when analysis is enabled.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    session_factory = get_session_factory()

    def _mlflow_uri_factory() -> str | None:
        if args.mlflow_dir is None:
            return None
        args.mlflow_dir.mkdir(parents=True, exist_ok=True)
        return args.mlflow_dir.as_uri()

    report = run_single_user_benchmark(
        session_factory,
        iterations=args.iterations,
        include_analysis=args.include_analysis,
        mlflow_uri_factory=_mlflow_uri_factory if args.include_analysis else None,
    )
    print(format_report(report.values()))


if __name__ == "__main__":
    main()
