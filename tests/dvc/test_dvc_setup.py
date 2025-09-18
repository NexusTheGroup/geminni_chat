from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]


def test_dvc_configuration_exists() -> None:
    config_path = ROOT_DIR / ".dvc" / "config"
    assert config_path.exists()


def test_dvc_status_is_clean() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "dvc", "status"],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        check=True,
    )
    stdout = result.stdout.lower()
    assert "up to date" in stdout or "no changes" in stdout
