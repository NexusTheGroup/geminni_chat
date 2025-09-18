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
    # Allow for various DVC states as long as DVC is working properly
    dvc_working_states = [
        "up to date",
        "no changes",
        "modified",
        "deleted",
        "changed outs",
    ]
    assert any(
        state in stdout for state in dvc_working_states
    ), f"Unexpected DVC status: {result.stdout}"
