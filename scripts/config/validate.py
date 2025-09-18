#!/usr/bin/env python3
"""Validate application configuration and optionally print resolved values."""

from __future__ import annotations

import argparse
import json
import sys

from nexus_knowledge.config import ConfigurationError, reload_settings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output resolved configuration as JSON (with secrets redacted).",
    )
    args = parser.parse_args(argv)

    try:
        settings = reload_settings()
    except ConfigurationError as exc:
        sys.stderr.write("Configuration validation failed:\n")
        for message in exc.errors:
            sys.stderr.write(f"  - {message}\n")
        return 1

    if args.json:
        payload = settings.model_dump(by_alias=True)
        payload["SECRET_KEY"] = "*** redacted ***"
        sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
        sys.stdout.write("\n")
    else:
        sys.stdout.write("Configuration OK for environment: ")
        sys.stdout.write(f"{settings.app_env!r}\n")

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
