#!/usr/bin/env python3
"""Run Alembic migrations for the NexusKnowledge project."""

from __future__ import annotations

import argparse
from pathlib import Path

from alembic import command
from alembic.config import Config

ROOT_DIR = Path(__file__).resolve().parent.parent


def _load_config() -> Config:
    config_path = ROOT_DIR / "alembic.ini"
    cfg = Config(str(config_path))
    cfg.set_main_option("script_location", str(ROOT_DIR / "alembic"))
    return cfg


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Alembic migrations.")
    parser.add_argument(
        "revision", nargs="?", default="head", help="Target revision (default: head)",
    )
    parser.add_argument(
        "--downgrade", action="store_true", help="Downgrade instead of upgrade.",
    )
    args = parser.parse_args()

    cfg = _load_config()

    if args.downgrade:
        command.downgrade(cfg, args.revision)
    else:
        command.upgrade(cfg, args.revision)


if __name__ == "__main__":
    main()
