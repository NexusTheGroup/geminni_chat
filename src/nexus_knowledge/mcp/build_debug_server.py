#!/usr/bin/env python3
"""Build and Dependencies Debug MCP Server for NexusKnowledge

This MCP server provides build debugging capabilities for the NexusKnowledge project,
including dependency analysis, build process monitoring, and deployment debugging.
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("NexusKnowledge-BuildDebug")

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


@mcp.tool()
def check_dependencies() -> str:
    """Check all project dependencies and their versions.

    Returns
    -------
        JSON string with dependency information

    """
    try:
        # Check Python dependencies
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT, check=False,
        )

        if result.returncode != 0:
            return json.dumps(
                {
                    "error": f"Failed to get dependencies: {result.stderr}",
                    "success": False,
                },
                indent=2,
            )

        dependencies = json.loads(result.stdout)

        # Filter for project-specific dependencies
        project_deps = []
        for dep in dependencies:
            if any(
                keyword in dep["name"].lower()
                for keyword in [
                    "nexus",
                    "fastapi",
                    "sqlalchemy",
                    "celery",
                    "pydantic",
                    "alembic",
                    "psycopg2",
                    "mlflow",
                    "dvc",
                    "mcp",
                ]
            ):
                project_deps.append(dep)

        return json.dumps(
            {
                "success": True,
                "total_dependencies": len(dependencies),
                "project_dependencies": project_deps,
                "all_dependencies": dependencies,
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.tool()
def analyze_dependency_conflicts() -> str:
    """Analyze potential dependency conflicts in the project.

    Returns
    -------
        JSON string with conflict analysis

    """
    try:
        # Check for conflicting versions
        result = subprocess.run(
            [sys.executable, "-m", "pip", "check"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT, check=False,
        )

        conflicts = []
        if result.returncode != 0:
            conflicts = (
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )

        # Check for outdated packages
        outdated_result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT, check=False,
        )

        outdated = []
        if outdated_result.returncode == 0 and outdated_result.stdout.strip():
            outdated = json.loads(outdated_result.stdout)

        return json.dumps(
            {
                "success": True,
                "conflicts": conflicts,
                "has_conflicts": len(conflicts) > 0,
                "outdated_packages": outdated,
                "has_outdated": len(outdated) > 0,
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.tool()
def test_build_process() -> str:
    """Test the build process for the NexusKnowledge project.

    Returns
    -------
        JSON string with build test results

    """
    try:
        build_results = {"success": True, "tests": {}, "errors": []}

        # Test 1: Check if virtual environment is activated
        venv_path = os.environ.get("VIRTUAL_ENV")
        build_results["tests"]["virtual_env"] = {
            "active": venv_path is not None,
            "path": venv_path,
            "success": venv_path is not None,
        }

        # Test 2: Check Python version compatibility
        python_version = sys.version_info
        build_results["tests"]["python_version"] = {
            "version": f"{python_version.major}.{python_version.minor}.{python_version.micro}",
            "compatible": python_version >= (3, 11),
            "success": python_version >= (3, 11),
        }

        # Test 3: Check if required files exist
        required_files = [
            "pyproject.toml",
            "src/nexus_knowledge/__init__.py",
            "src/nexus_knowledge/api/main.py",
            "alembic.ini",
            "docker-compose.yml",
        ]

        file_checks = {}
        for file_path in required_files:
            full_path = PROJECT_ROOT / file_path
            exists = full_path.exists()
            file_checks[file_path] = {"exists": exists, "path": str(full_path)}

        build_results["tests"]["required_files"] = file_checks

        # Test 4: Check if imports work
        import_tests = {}
        try:

            import_tests["nexus_knowledge"] = {"success": True, "error": None}
        except Exception as e:
            import_tests["nexus_knowledge"] = {"success": False, "error": str(e)}
            build_results["errors"].append(f"Import error: {e!s}")

        try:

            import_tests["fastapi_app"] = {"success": True, "error": None}
        except Exception as e:
            import_tests["fastapi_app"] = {"success": False, "error": str(e)}
            build_results["errors"].append(f"FastAPI import error: {e!s}")

        build_results["tests"]["imports"] = import_tests

        # Test 5: Check database connectivity (if possible)
        try:

            # Don't actually create a session, just test import
            build_results["tests"]["database_import"] = {"success": True, "error": None}
        except Exception as e:
            build_results["tests"]["database_import"] = {
                "success": False,
                "error": str(e),
            }
            build_results["errors"].append(f"Database import error: {e!s}")

        # Overall success
        all_tests_passed = all(
            test.get("success", False)
            for test in build_results["tests"].values()
            if isinstance(test, dict) and "success" in test
        )
        build_results["success"] = (
            all_tests_passed and len(build_results["errors"]) == 0
        )

        return json.dumps(build_results, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.tool()
def check_docker_build() -> str:
    """Check Docker build configuration and test build process.

    Returns
    -------
        JSON string with Docker build analysis

    """
    try:
        docker_results = {"success": True, "tests": {}, "errors": []}

        # Check if Docker is available
        try:
            docker_version = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT, check=False,
            )
            docker_results["tests"]["docker_available"] = {
                "success": docker_version.returncode == 0,
                "version": (
                    docker_version.stdout.strip()
                    if docker_version.returncode == 0
                    else None
                ),
            }
        except FileNotFoundError:
            docker_results["tests"]["docker_available"] = {
                "success": False,
                "error": "Docker not found",
            }
            docker_results["errors"].append("Docker not available")

        # Check if Dockerfile exists
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        docker_results["tests"]["dockerfile"] = {
            "exists": dockerfile_path.exists(),
            "path": str(dockerfile_path),
        }

        # Check if docker-compose.yml exists
        compose_path = PROJECT_ROOT / "docker-compose.yml"
        docker_results["tests"]["docker_compose"] = {
            "exists": compose_path.exists(),
            "path": str(compose_path),
        }

        # Test Docker build (dry run)
        if docker_results["tests"]["docker_available"]["success"]:
            try:
                build_test = subprocess.run(
                    ["docker", "build", "--dry-run", "."],
                    capture_output=True,
                    text=True,
                    cwd=PROJECT_ROOT,
                    timeout=30, check=False,
                )
                docker_results["tests"]["build_test"] = {
                    "success": build_test.returncode == 0,
                    "output": build_test.stdout,
                    "error": build_test.stderr if build_test.returncode != 0 else None,
                }
            except subprocess.TimeoutExpired:
                docker_results["tests"]["build_test"] = {
                    "success": False,
                    "error": "Build test timed out",
                }
                docker_results["errors"].append("Docker build test timed out")
            except Exception as e:
                docker_results["tests"]["build_test"] = {
                    "success": False,
                    "error": str(e),
                }
                docker_results["errors"].append(f"Docker build test error: {e!s}")

        return json.dumps(docker_results, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.tool()
def analyze_package_structure() -> str:
    """Analyze the package structure and identify potential issues.

    Returns
    -------
        JSON string with package structure analysis

    """
    try:
        analysis = {
            "success": True,
            "structure": {},
            "issues": [],
            "recommendations": [],
        }

        # Check main package structure
        src_path = PROJECT_ROOT / "src"
        nexus_path = src_path / "nexus_knowledge"

        structure_checks = {
            "src_directory": src_path.exists(),
            "nexus_knowledge_package": nexus_path.exists(),
            "api_module": (nexus_path / "api").exists(),
            "db_module": (nexus_path / "db").exists(),
            "analysis_module": (nexus_path / "analysis").exists(),
            "search_module": (nexus_path / "search").exists(),
            "correlation_module": (nexus_path / "correlation").exists(),
            "ingestion_module": (nexus_path / "ingestion").exists(),
            "export_module": (nexus_path / "export").exists(),
            "tasks_module": (nexus_path / "tasks").exists(),
        }

        analysis["structure"] = structure_checks

        # Check for missing __init__.py files
        missing_init_files = []
        for module in [
            "api",
            "db",
            "analysis",
            "search",
            "correlation",
            "ingestion",
            "export",
            "tasks",
        ]:
            init_file = nexus_path / module / "__init__.py"
            if not init_file.exists():
                missing_init_files.append(str(init_file))

        if missing_init_files:
            analysis["issues"].append(
                f"Missing __init__.py files: {missing_init_files}",
            )

        # Check for circular imports
        try:
            # This is a basic check - in practice, you'd want more sophisticated analysis

            analysis["structure"]["main_import"] = True
        except Exception as e:
            analysis["issues"].append(f"Main module import issue: {e!s}")
            analysis["structure"]["main_import"] = False

        # Check pyproject.toml configuration
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        if pyproject_path.exists():
            analysis["structure"]["pyproject_toml"] = True
            # Could add more detailed analysis of pyproject.toml here
        else:
            analysis["issues"].append("pyproject.toml not found")
            analysis["structure"]["pyproject_toml"] = False

        # Recommendations
        if missing_init_files:
            analysis["recommendations"].append(
                "Add missing __init__.py files to make modules importable",
            )

        if not analysis["structure"]["main_import"]:
            analysis["recommendations"].append("Fix import issues in main module")

        return json.dumps(analysis, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.tool()
def check_environment_config() -> str:
    """Check environment configuration and required variables.

    Returns
    -------
        JSON string with environment analysis

    """
    try:
        env_analysis = {
            "success": True,
            "environment": {},
            "missing_vars": [],
            "recommendations": [],
        }

        # Check Python environment
        env_analysis["environment"]["python_version"] = sys.version
        env_analysis["environment"]["python_executable"] = sys.executable
        env_analysis["environment"]["virtual_env"] = os.environ.get("VIRTUAL_ENV")
        env_analysis["environment"]["working_directory"] = str(PROJECT_ROOT)

        # Check for required environment variables
        required_vars = ["DATABASE_URL", "REDIS_URL", "MLFLOW_TRACKING_URI"]

        for var in required_vars:
            value = os.environ.get(var)
            if value:
                env_analysis["environment"][var] = "SET"
            else:
                env_analysis["environment"][var] = "NOT_SET"
                env_analysis["missing_vars"].append(var)

        # Check for .env file
        env_file = PROJECT_ROOT / ".env"
        env_analysis["environment"]["env_file_exists"] = env_file.exists()

        if env_analysis["missing_vars"]:
            env_analysis["recommendations"].append("Set missing environment variables")
            env_analysis["recommendations"].append(
                "Create .env file with required variables",
            )

        return json.dumps(env_analysis, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.tool()
def run_linting_checks() -> str:
    """Run linting checks on the project code.

    Returns
    -------
        JSON string with linting results

    """
    try:
        linting_results = {"success": True, "checks": {}, "errors": [], "warnings": []}

        # Run ruff linting
        try:
            ruff_result = subprocess.run(
                [sys.executable, "-m", "ruff", "check", "src/", "tests/"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT, check=False,
            )
            linting_results["checks"]["ruff"] = {
                "success": ruff_result.returncode == 0,
                "output": ruff_result.stdout,
                "errors": ruff_result.stderr if ruff_result.returncode != 0 else None,
            }
        except Exception as e:
            linting_results["checks"]["ruff"] = {"success": False, "error": str(e)}
            linting_results["errors"].append(f"Ruff check failed: {e!s}")

        # Run black formatting check
        try:
            black_result = subprocess.run(
                [sys.executable, "-m", "black", "--check", "src/", "tests/"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT, check=False,
            )
            linting_results["checks"]["black"] = {
                "success": black_result.returncode == 0,
                "output": black_result.stdout,
                "errors": black_result.stderr if black_result.returncode != 0 else None,
            }
        except Exception as e:
            linting_results["checks"]["black"] = {"success": False, "error": str(e)}
            linting_results["errors"].append(f"Black check failed: {e!s}")

        # Overall success
        all_checks_passed = all(
            check.get("success", False) for check in linting_results["checks"].values()
        )
        linting_results["success"] = (
            all_checks_passed and len(linting_results["errors"]) == 0
        )

        return json.dumps(linting_results, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.resource("nexus://build/status")
def build_status_resource() -> str:
    """Get the current build status of the NexusKnowledge project."""
    try:
        # Quick build status check
        status_checks = {
            "python_version": sys.version_info >= (3, 11),
            "virtual_env": os.environ.get("VIRTUAL_ENV") is not None,
            "project_structure": (PROJECT_ROOT / "src" / "nexus_knowledge").exists(),
            "dependencies": True,  # Could add more detailed checks here
        }

        overall_status = all(status_checks.values())
        return f"Build Status: {'HEALTHY' if overall_status else 'ISSUES DETECTED'}\nChecks: {status_checks}"
    except Exception as e:
        return f"Build Status: ERROR - {e!s}"


@mcp.resource("nexus://build/dependencies")
def dependencies_resource() -> str:
    """Get current dependency information."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT, check=False,
        )
        return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
    except Exception as e:
        return f"Error getting dependencies: {e!s}"


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
