from __future__ import annotations

import contextlib
import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_ARTIFACT = ROOT_DIR / "data" / "processed" / "sample_data.json"


def _cleanup_artifact() -> None:
    if DATA_ARTIFACT.exists():
        DATA_ARTIFACT.unlink()
    parent = DATA_ARTIFACT.parent
    with contextlib.suppress(OSError):
        parent.rmdir()


def test_dvc_repro_pipeline_creates_artifact() -> None:
    _cleanup_artifact()
    subprocess.run(
        [sys.executable, "-m", "dvc", "repro", "prepare_sample"],
        cwd=ROOT_DIR,
        check=True,
        env={**os.environ},
    )
    assert DATA_ARTIFACT.exists()
    _cleanup_artifact()
