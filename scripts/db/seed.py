#!/usr/bin/env python3
"""Seed the database with sample raw data."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

from nexus_knowledge.config import reload_settings
from nexus_knowledge.db.session import get_session_factory
from nexus_knowledge.ingestion import ingest_raw_payload
from nexus_knowledge.ingestion.service import normalize_raw_data

DEFAULT_SAMPLE = Path("sample_data.json")


def _load_payloads(path: Path) -> list[dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [payload for payload in data if isinstance(payload, dict)]
    if isinstance(data, dict):
        return [data]
    raise ValueError("Seed file must contain an object or a list of objects")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_SAMPLE,
        help="Path to JSON seed data (default: sample_data.json).",
    )
    parser.add_argument(
        "--source-type",
        default="seed",
        help="Source type label stored with the raw payload (default: seed).",
    )
    parser.add_argument(
        "--normalize",
        action="store_true",
        help="Normalize conversations immediately after ingestion.",
    )
    args = parser.parse_args(argv)

    if not args.path.exists():
        sys.stderr.write(f"Seed file not found: {args.path}\n")
        return 1

    reload_settings()
    session_factory = get_session_factory()

    payloads = _load_payloads(args.path)
    inserted: list[uuid.UUID] = []

    for payload in payloads:
        with session_factory.begin() as session:
            raw_id = ingest_raw_payload(
                session,
                source_type=args.source_type,
                content=payload,
            )
            inserted.append(raw_id)
            if args.normalize:
                normalize_raw_data(session, raw_id)

    sys.stdout.write(
        f"Inserted {len(inserted)} payload(s) from {args.path} as source '{args.source_type}'.\n",
    )
    if args.normalize:
        sys.stdout.write("Normalization completed for all inserted payloads.\n")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
