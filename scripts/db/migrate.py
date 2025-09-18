#!/usr/bin/env python3
"""Convenience wrapper around the Alembic migration runner."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("revision", nargs="?", default="head")
    parser.add_argument(
        "--downgrade",
        action="store_true",
        help="Downgrade instead of upgrade",
    )
    args = parser.parse_args(argv)

    cmd = [sys.executable, str(ROOT / "scripts" / "run_migrations.py"), args.revision]
    if args.downgrade:
        cmd.append("--downgrade")

    completed = subprocess.run(cmd, cwd=ROOT, check=False)
    return completed.returncode


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
