"""Generate a processed sample dataset for DVC pipelines."""

from __future__ import annotations

import argparse
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare processed sample data for the DVC pipeline.",
    )
    parser.add_argument("--input", required=True, help="Source JSON file to copy from.")
    parser.add_argument(
        "--output",
        required=True,
        help="Destination path for the processed artifact.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    source = Path(args.input)
    target = Path(args.output)
    if not source.exists():
        raise FileNotFoundError(f"Input file not found: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


if __name__ == "__main__":
    main()
