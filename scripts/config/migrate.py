#!/usr/bin/env python3
"""Compare current environment with the documented configuration schema."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from nexus_knowledge.config import ConfigurationError, Settings, reload_settings

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "config" / "schema.json"


def _load_schema() -> dict[str, object]:
    try:
        return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"Missing schema file at {SCHEMA_PATH}") from exc


def _alias_map() -> dict[str, str]:
    return {
        (field.alias or name).upper(): name
        for name, field in Settings.model_fields.items()
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--env",
        choices=["local", "test", "prod"],
        help="Override detected environment when evaluating schema.",
    )
    args = parser.parse_args(argv)

    schema = _load_schema()
    alias_map = _alias_map()

    try:
        settings = reload_settings()
    except ConfigurationError as exc:
        sys.stderr.write("Unable to evaluate config — base validation failed:\n")
        for message in exc.errors:
            sys.stderr.write(f"  - {message}\n")
        return 1

    app_env = args.env or settings.app_env

    missing: list[str] = []
    warnings: list[str] = []

    for field in schema.get("fields", []):
        name = field["name"].upper()
        attr = alias_map.get(name)
        requirement = field.get("environments", {}).get(app_env, "optional").lower()
        is_required = requirement == "required"
        current = getattr(settings, attr, None)

        if is_required and (current is None or current == ""):
            missing.append(f"{name} is required in {app_env} environments")

        if field.get("deprecated"):
            warnings.append(f"{name} is marked as deprecated: {field['deprecated']}")

    if missing:
        sys.stderr.write("Missing configuration detected:\n")
        for message in missing:
            sys.stderr.write(f"  - {message}\n")
        return 2

    if warnings:
        sys.stdout.write("Warnings:\n")
        for message in warnings:
            sys.stdout.write(f"  - {message}\n")

    sys.stdout.write(
        f"Configuration schema check passed for environment '{app_env}'.\n",
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
