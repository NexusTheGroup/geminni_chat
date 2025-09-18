#!/usr/bin/env python3
"""GitHub MCP Server for NexusKnowledge.

This MCP server provides GitHub integration capabilities for the NexusKnowledge project,
including repository management, issue tracking, and CI/CD monitoring.
"""

import json
import logging
import os
import subprocess
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("NexusKnowledge-GitHub")

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# GitHub API configuration
GITHUB_API_BASE = "https://api.github.com"
GITHUB_PAT_KEY = os.environ.get("GITHUB_PAT_KEY")
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "NexusTheGroup/geminni_chat")


@mcp.tool()
def get_repository_info() -> str:
    """Get information about the NexusKnowledge repository.

    Returns
    -------
        JSON string with repository information

    """
    try:
        if not GITHUB_PAT_KEY:
            return json.dumps(
                {
                    "error": "GITHUB_PAT_KEY environment variable not set",
                    "success": False,
                },
                indent=2,
            )

        headers = {
            "Authorization": f"token {GITHUB_PAT_KEY}",
            "Accept": "application/vnd.github.v3+json",
        }

        response = httpx.get(f"{GITHUB_API_BASE}/repos/{GITHUB_REPO}", headers=headers)

        if response.status_code == 200:
            repo_data = response.json()
            return json.dumps(
                {
                    "success": True,
                    "repository": {
                        "name": repo_data["name"],
                        "full_name": repo_data["full_name"],
                        "description": repo_data["description"],
                        "url": repo_data["html_url"],
                        "stars": repo_data["stargazers_count"],
                        "forks": repo_data["forks_count"],
                        "open_issues": repo_data["open_issues_count"],
                        "language": repo_data["language"],
                        "created_at": repo_data["created_at"],
                        "updated_at": repo_data["updated_at"],
                    },
                },
                indent=2,
            )
        return json.dumps(
            {
                "error": f"GitHub API error: {response.status_code}",
                "success": False,
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.tool()
def list_recent_commits(limit: int = 10) -> str:
    """List recent commits from the repository.

    Args:
    ----
        limit: Maximum number of commits to retrieve

    Returns:
    -------
        JSON string with commit information

    """
    try:
        if not GITHUB_PAT_KEY:
            return json.dumps(
                {
                    "error": "GITHUB_PAT_KEY environment variable not set",
                    "success": False,
                },
                indent=2,
            )

        headers = {
            "Authorization": f"token {GITHUB_PAT_KEY}",
            "Accept": "application/vnd.github.v3+json",
        }

        response = httpx.get(
            f"{GITHUB_API_BASE}/repos/{GITHUB_REPO}/commits",
            headers=headers,
            params={"per_page": limit},
        )

        if response.status_code == 200:
            commits = response.json()
            commit_list = []

            for commit in commits:
                commit_list.append(
                    {
                        "sha": commit["sha"][:7],
                        "message": commit["commit"]["message"],
                        "author": commit["commit"]["author"]["name"],
                        "date": commit["commit"]["author"]["date"],
                        "url": commit["html_url"],
                    },
                )

            return json.dumps(
                {"success": True, "commits": commit_list, "count": len(commit_list)},
                indent=2,
            )
        return json.dumps(
            {
                "error": f"GitHub API error: {response.status_code}",
                "success": False,
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.tool()
def list_open_issues(limit: int = 10) -> str:
    """List open issues from the repository.

    Args:
    ----
        limit: Maximum number of issues to retrieve

    Returns:
    -------
        JSON string with issue information

    """
    try:
        if not GITHUB_PAT_KEY:
            return json.dumps(
                {
                    "error": "GITHUB_PAT_KEY environment variable not set",
                    "success": False,
                },
                indent=2,
            )

        headers = {
            "Authorization": f"token {GITHUB_PAT_KEY}",
            "Accept": "application/vnd.github.v3+json",
        }

        response = httpx.get(
            f"{GITHUB_API_BASE}/repos/{GITHUB_REPO}/issues",
            headers=headers,
            params={"state": "open", "per_page": limit},
        )

        if response.status_code == 200:
            issues = response.json()
            issue_list = []

            for issue in issues:
                issue_list.append(
                    {
                        "number": issue["number"],
                        "title": issue["title"],
                        "body": (
                            issue["body"][:200] + "..."
                            if issue["body"] and len(issue["body"]) > 200
                            else issue["body"]
                        ),
                        "state": issue["state"],
                        "labels": [label["name"] for label in issue["labels"]],
                        "assignee": (
                            issue["assignee"]["login"] if issue["assignee"] else None
                        ),
                        "created_at": issue["created_at"],
                        "updated_at": issue["updated_at"],
                        "url": issue["html_url"],
                    },
                )

            return json.dumps(
                {"success": True, "issues": issue_list, "count": len(issue_list)},
                indent=2,
            )
        return json.dumps(
            {
                "error": f"GitHub API error: {response.status_code}",
                "success": False,
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.tool()
def list_pull_requests(limit: int = 10) -> str:
    """List pull requests from the repository.

    Args:
    ----
        limit: Maximum number of PRs to retrieve

    Returns:
    -------
        JSON string with PR information

    """
    try:
        if not GITHUB_PAT_KEY:
            return json.dumps(
                {
                    "error": "GITHUB_PAT_KEY environment variable not set",
                    "success": False,
                },
                indent=2,
            )

        headers = {
            "Authorization": f"token {GITHUB_PAT_KEY}",
            "Accept": "application/vnd.github.v3+json",
        }

        response = httpx.get(
            f"{GITHUB_API_BASE}/repos/{GITHUB_REPO}/pulls",
            headers=headers,
            params={"state": "all", "per_page": limit},
        )

        if response.status_code == 200:
            prs = response.json()
            pr_list = []

            for pr in prs:
                pr_list.append(
                    {
                        "number": pr["number"],
                        "title": pr["title"],
                        "body": (
                            pr["body"][:200] + "..."
                            if pr["body"] and len(pr["body"]) > 200
                            else pr["body"]
                        ),
                        "state": pr["state"],
                        "head_branch": pr["head"]["ref"],
                        "base_branch": pr["base"]["ref"],
                        "author": pr["user"]["login"],
                        "created_at": pr["created_at"],
                        "updated_at": pr["updated_at"],
                        "url": pr["html_url"],
                    },
                )

            return json.dumps(
                {"success": True, "pull_requests": pr_list, "count": len(pr_list)},
                indent=2,
            )
        return json.dumps(
            {
                "error": f"GitHub API error: {response.status_code}",
                "success": False,
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.tool()
def check_github_actions_status() -> str:
    """Check the status of GitHub Actions workflows.

    Returns
    -------
        JSON string with workflow status

    """
    try:
        if not GITHUB_PAT_KEY:
            return json.dumps(
                {
                    "error": "GITHUB_PAT_KEY environment variable not set",
                    "success": False,
                },
                indent=2,
            )

        headers = {
            "Authorization": f"token {GITHUB_PAT_KEY}",
            "Accept": "application/vnd.github.v3+json",
        }

        response = httpx.get(
            f"{GITHUB_API_BASE}/repos/{GITHUB_REPO}/actions/runs",
            headers=headers,
            params={"per_page": 10},
        )

        if response.status_code == 200:
            runs = response.json()
            workflow_list = []

            for run in runs["workflow_runs"]:
                workflow_list.append(
                    {
                        "id": run["id"],
                        "name": run["name"],
                        "status": run["status"],
                        "conclusion": run["conclusion"],
                        "head_branch": run["head_branch"],
                        "created_at": run["created_at"],
                        "updated_at": run["updated_at"],
                        "url": run["html_url"],
                    },
                )

            return json.dumps(
                {
                    "success": True,
                    "workflows": workflow_list,
                    "count": len(workflow_list),
                },
                indent=2,
            )
        return json.dumps(
            {
                "error": f"GitHub API error: {response.status_code}",
                "success": False,
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.tool()
def get_local_git_status() -> str:
    """Get the local git status of the NexusKnowledge project.

    Returns
    -------
        JSON string with git status information

    """
    try:
        git_status = {"success": True, "git_info": {}}

        # Get current branch
        try:
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
                check=False,
            )
            git_status["git_info"]["current_branch"] = branch_result.stdout.strip()
        except Exception as e:
            git_status["git_info"]["current_branch"] = f"Error: {e!s}"

        # Get git status
        try:
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
                check=False,
            )
            git_status["git_info"]["status"] = (
                status_result.stdout.strip().split("\n")
                if status_result.stdout.strip()
                else []
            )
        except Exception as e:
            git_status["git_info"]["status"] = f"Error: {e!s}"

        # Get last commit
        try:
            commit_result = subprocess.run(
                ["git", "log", "-1", "--oneline"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
                check=False,
            )
            git_status["git_info"]["last_commit"] = commit_result.stdout.strip()
        except Exception as e:
            git_status["git_info"]["last_commit"] = f"Error: {e!s}"

        # Get remote URL
        try:
            remote_result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
                check=False,
            )
            git_status["git_info"]["remote_url"] = remote_result.stdout.strip()
        except Exception as e:
            git_status["git_info"]["remote_url"] = f"Error: {e!s}"

        return json.dumps(git_status, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.tool()
def create_issue(title: str, body: str, labels: list[str] | None = None) -> str:
    """Create a new GitHub issue.

    Args:
    ----
        title: Issue title
        body: Issue description
        labels: Optional list of labels

    Returns:
    -------
        JSON string with issue creation result

    """
    try:
        if not GITHUB_PAT_KEY:
            return json.dumps(
                {
                    "error": "GITHUB_PAT_KEY environment variable not set",
                    "success": False,
                },
                indent=2,
            )

        headers = {
            "Authorization": f"token {GITHUB_PAT_KEY}",
            "Accept": "application/vnd.github.v3+json",
        }

        issue_data = {"title": title, "body": body}

        if labels:
            issue_data["labels"] = labels

        response = httpx.post(
            f"{GITHUB_API_BASE}/repos/{GITHUB_REPO}/issues",
            headers=headers,
            json=issue_data,
        )

        if response.status_code == 201:
            issue = response.json()
            return json.dumps(
                {
                    "success": True,
                    "issue": {
                        "number": issue["number"],
                        "title": issue["title"],
                        "url": issue["html_url"],
                        "state": issue["state"],
                    },
                },
                indent=2,
            )
        return json.dumps(
            {
                "error": f"GitHub API error: {response.status_code} - {response.text}",
                "success": False,
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.resource("github://repo/info")
def repository_info_resource() -> str:
    """Get current repository information."""
    try:
        result = get_repository_info()
        data = json.loads(result)
        if data.get("success"):
            repo = data["repository"]
            return f"Repository: {repo['full_name']}\nDescription: {repo['description']}\nStars: {repo['stars']}\nOpen Issues: {repo['open_issues']}"
        return f"Error: {data.get('error', 'Unknown error')}"
    except Exception as e:
        return f"Error getting repository info: {e!s}"


@mcp.resource("github://repo/status")
def repository_status_resource() -> str:
    """Get current repository status."""
    try:
        result = get_local_git_status()
        data = json.loads(result)
        if data.get("success"):
            git_info = data["git_info"]
            return f"Branch: {git_info.get('current_branch', 'Unknown')}\nLast Commit: {git_info.get('last_commit', 'Unknown')}\nRemote: {git_info.get('remote_url', 'Unknown')}"
        return f"Error: {data.get('error', 'Unknown error')}"
    except Exception as e:
        return f"Error getting repository status: {e!s}"


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
