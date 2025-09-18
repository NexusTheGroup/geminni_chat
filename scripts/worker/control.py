#!/usr/bin/env python3
"""Simple CLI for interacting with the Celery worker."""

from __future__ import annotations

import argparse
import json
import sys

from nexus_knowledge.tasks import celery_app


def _print(obj: object) -> None:
    sys.stdout.write(json.dumps(obj, indent=2, default=str))
    sys.stdout.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("ping", help="Ping available workers.")
    sub.add_parser("stats", help="Show worker statistics.")
    sub.add_parser("active", help="List active tasks.")
    sub.add_parser("purge", help="Purge all tasks from the default queue.")

    args = parser.parse_args(argv)
    inspect = celery_app.control.inspect()

    if args.command == "ping":
        _print(celery_app.control.ping())
    elif args.command == "stats":
        _print(inspect.stats() or {})
    elif args.command == "active":
        _print(inspect.active() or {})
    elif args.command == "purge":
        count = celery_app.control.purge()
        sys.stdout.write(f"Purged {count} message(s).\n")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
