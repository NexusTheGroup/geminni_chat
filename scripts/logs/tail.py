#!/usr/bin/env python3
"""Tail a log file with optional follow mode."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


def _tail(path: Path, lines: int) -> list[str]:
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        return handle.readlines()[-lines:]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Path to the log file.")
    parser.add_argument(
        "--lines",
        type=int,
        default=100,
        help="Number of lines to show (default: 100).",
    )
    parser.add_argument(
        "--follow",
        action="store_true",
        help="Follow the file for new entries.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Refresh interval when following.",
    )
    args = parser.parse_args(argv)

    if not args.path.exists():
        sys.stderr.write(f"Log file not found: {args.path}\n")
        return 1

    for line in _tail(args.path, args.lines):
        sys.stdout.write(line)
    sys.stdout.flush()

    if not args.follow:
        return 0

    with args.path.open("r", encoding="utf-8", errors="ignore") as handle:
        handle.seek(0, 2)
        try:
            while True:
                chunk = handle.readline()
                if chunk:
                    sys.stdout.write(chunk)
                    sys.stdout.flush()
                else:
                    time.sleep(args.interval)
        except KeyboardInterrupt:  # pragma: no cover - interactive use
            return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
