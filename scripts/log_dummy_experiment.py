#!/usr/bin/env python3
"""CLI helper to log a dummy MLflow experiment."""

from __future__ import annotations

import argparse
from pathlib import Path

from nexus_knowledge.mlflow_utils import ensure_local_store_exists, log_dummy_experiment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Log a dummy MLflow experiment for smoke testing.",
    )
    parser.add_argument("--uri", help="Optional override for the MLflow tracking URI.")
    parser.add_argument(
        "--artifact-dir",
        help="Optional path for local artifact storage when using a file backend.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.artifact_dir:
        ensure_local_store_exists(Path(args.artifact_dir))

    run_id = log_dummy_experiment(parameters={"cli": True}, tracking_uri=args.uri)

    print(f"Logged MLflow run with ID: {run_id}")


if __name__ == "__main__":
    main()
