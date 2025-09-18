#!/usr/bin/env python3
"""Perform health checks against the running API."""

from __future__ import annotations

import argparse
import sys

import httpx
from nexus_knowledge.config import get_settings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000).",
    )
    args = parser.parse_args(argv)

    settings = get_settings()
    readiness_url = f"{args.base_url}{settings.api_root}/health/ready"
    liveness_url = f"{args.base_url}{settings.api_root}/health/live"

    with httpx.Client(timeout=5.0) as client:
        live_response = client.get(liveness_url)
        ready_response = client.get(readiness_url)

    sys.stdout.write(
        f"Live: {live_response.status_code} {live_response.text}\n"
        f"Ready: {ready_response.status_code} {ready_response.text}\n",
    )

    if live_response.is_error or ready_response.is_error:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
