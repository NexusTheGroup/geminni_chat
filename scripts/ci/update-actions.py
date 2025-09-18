#!/usr/bin/env python3
"""Script to automatically update GitHub Actions to their latest versions."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import requests

# Common GitHub Actions and their repositories
ACTIONS_MAP = {
    "actions/checkout": "actions/checkout",
    "actions/setup-python": "actions/setup-python",
    "actions/setup-node": "actions/setup-node",
    "actions/cache": "actions/cache",
    "actions/upload-artifact": "actions/upload-artifact",
    "actions/download-artifact": "actions/download-artifact",
    "github/codeql-action": "github/codeql-action",
}


def get_latest_release(repo: str) -> str:
    """Get the latest release tag for a GitHub repository."""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()["tag_name"]
    except Exception as e:
        print(f"Failed to get latest release for {repo}: {e}")
        return ""


def update_workflow_file(file_path: Path) -> bool:
    """Update a single workflow file with latest action versions."""
    content = file_path.read_text()
    updated = False

    for action_name, repo in ACTIONS_MAP.items():
        latest_version = get_latest_release(repo)
        if not latest_version:
            continue

        # Pattern to match: uses: action/name@version
        pattern = rf"(uses:\s+{re.escape(action_name)})@[\w.-]+"
        replacement = rf"\1@{latest_version}"

        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            print(f"Updated {action_name} to {latest_version} in {file_path.name}")
            content = new_content
            updated = True

    if updated:
        file_path.write_text(content)

    return updated


def main() -> int:
    """Main function to update all workflow files."""
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        print("No .github/workflows directory found")
        return 1

    updated_files = []
    for workflow_file in workflows_dir.glob("*.yml"):
        if update_workflow_file(workflow_file):
            updated_files.append(workflow_file.name)

    if updated_files:
        print(f"\nUpdated {len(updated_files)} workflow files:")
        for file_name in updated_files:
            print(f"  - {file_name}")

        # Optionally run actionlint to validate changes
        try:
            result = subprocess.run(
                ["actionlint", str(workflows_dir)],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                print("\n✅ All workflow files are valid")
            else:
                print(f"\n❌ Workflow validation failed:\n{result.stderr}")
                return 1
        except FileNotFoundError:
            print("\n⚠️  actionlint not found - skipping validation")
            print(
                "Install with: go install github.com/rhysd/actionlint/cmd/actionlint@latest",
            )
    else:
        print("No workflow files needed updating")

    return 0


if __name__ == "__main__":
    sys.exit(main())
