#!/usr/bin/env python3
"""Docker MCP Server for NexusKnowledge

This MCP server provides real-time Docker monitoring and troubleshooting capabilities
for the NexusKnowledge project, including container management, build monitoring,
and real-time debugging during Docker operations.
"""

import json
import logging
import subprocess
import time
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("NexusKnowledge-Docker")

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


@mcp.tool()
def get_docker_status() -> str:
    """Get the current status of all Docker containers and services.

    Returns
    -------
        JSON string with Docker status information

    """
    try:
        # Get container status
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "json"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT, check=False,
        )

        containers = []
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    containers.append(json.loads(line))

        # Get Docker Compose status
        compose_result = subprocess.run(
            ["docker-compose", "ps", "--format", "json"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT, check=False,
        )

        compose_services = []
        if compose_result.returncode == 0 and compose_result.stdout.strip():
            for line in compose_result.stdout.strip().split("\n"):
                if line.strip():
                    compose_services.append(json.loads(line))

        # Get system info
        system_result = subprocess.run(
            ["docker", "system", "df", "--format", "json"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT, check=False,
        )

        system_info = []
        if system_result.returncode == 0 and system_result.stdout.strip():
            for line in system_result.stdout.strip().split("\n"):
                if line.strip():
                    system_info.append(json.loads(line))

        return json.dumps(
            {
                "success": True,
                "containers": containers,
                "compose_services": compose_services,
                "system_info": system_info,
                "timestamp": time.time(),
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.tool()
def monitor_docker_build(build_context: str = ".") -> str:
    """Monitor Docker build process in real-time.

    Args:
    ----
        build_context: Docker build context directory

    Returns:
    -------
        JSON string with build monitoring information

    """
    try:
        # Start build process
        build_process = subprocess.Popen(
            ["docker", "build", "-t", "nexus-knowledge", build_context],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=PROJECT_ROOT,
        )

        build_output = []
        build_errors = []

        # Monitor build output
        while build_process.poll() is None:
            line = build_process.stdout.readline()
            if line:
                build_output.append(line.strip())
                logger.info(f"Build: {line.strip()}")

        # Get any remaining output
        stdout, stderr = build_process.communicate()
        if stdout:
            build_output.extend(stdout.strip().split("\n"))
        if stderr:
            build_errors.extend(stderr.strip().split("\n"))

        return json.dumps(
            {
                "success": build_process.returncode == 0,
                "return_code": build_process.returncode,
                "build_output": build_output,
                "build_errors": build_errors,
                "timestamp": time.time(),
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.tool()
def get_container_logs(container_name: str, lines: int = 100) -> str:
    """Get logs from a specific Docker container.

    Args:
    ----
        container_name: Name of the container
        lines: Number of log lines to retrieve

    Returns:
    -------
        JSON string with container logs

    """
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", str(lines), container_name],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT, check=False,
        )

        logs = result.stdout.split("\n") if result.stdout else []
        errors = result.stderr.split("\n") if result.stderr else []

        return json.dumps(
            {
                "success": result.returncode == 0,
                "container": container_name,
                "logs": logs,
                "errors": errors,
                "timestamp": time.time(),
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.tool()
def check_docker_health() -> str:
    """Check the health of all Docker services and containers.

    Returns
    -------
        JSON string with health status

    """
    try:
        health_status = {
            "success": True,
            "services": {},
            "overall_health": "healthy",
            "timestamp": time.time(),
        }

        # Check Docker Compose services
        services = ["app", "db", "redis", "mlflow", "worker"]

        for service in services:
            try:
                # Check if container is running
                result = subprocess.run(
                    ["docker-compose", "ps", service],
                    capture_output=True,
                    text=True,
                    cwd=PROJECT_ROOT, check=False,
                )

                if result.returncode == 0:
                    # Check container health
                    health_result = subprocess.run(
                        [
                            "docker",
                            "inspect",
                            f"nexus-{service}",
                            "--format",
                            "{{.State.Health.Status}}",
                        ],
                        capture_output=True,
                        text=True,
                        cwd=PROJECT_ROOT, check=False,
                    )

                    health_status["services"][service] = {
                        "running": "Up" in result.stdout,
                        "health": (
                            health_result.stdout.strip()
                            if health_result.returncode == 0
                            else "unknown"
                        ),
                        "status": result.stdout.strip(),
                    }
                else:
                    health_status["services"][service] = {
                        "running": False,
                        "health": "unknown",
                        "status": "not found",
                    }

            except Exception as e:
                health_status["services"][service] = {
                    "running": False,
                    "health": "error",
                    "status": f"Error: {e!s}",
                }

        # Determine overall health
        unhealthy_services = [
            service
            for service, status in health_status["services"].items()
            if not status["running"] or status["health"] not in ["healthy", "unknown"]
        ]

        if unhealthy_services:
            health_status["overall_health"] = "unhealthy"
            health_status["unhealthy_services"] = unhealthy_services

        return json.dumps(health_status, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.tool()
def restart_docker_services(services: list[str] | None = None) -> str:
    """Restart Docker services.

    Args:
    ----
        services: List of services to restart (default: all)

    Returns:
    -------
        JSON string with restart results

    """
    try:
        if services is None:
            services = ["app", "db", "redis", "mlflow", "worker"]

        restart_results = {}

        for service in services:
            try:
                result = subprocess.run(
                    ["docker-compose", "restart", service],
                    capture_output=True,
                    text=True,
                    cwd=PROJECT_ROOT, check=False,
                )

                restart_results[service] = {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else None,
                }

            except Exception as e:
                restart_results[service] = {"success": False, "error": str(e)}

        return json.dumps(
            {
                "success": True,
                "restart_results": restart_results,
                "timestamp": time.time(),
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.tool()
def analyze_docker_performance() -> str:
    """Analyze Docker performance and resource usage.

    Returns
    -------
        JSON string with performance analysis

    """
    try:
        performance_data = {
            "success": True,
            "containers": {},
            "system": {},
            "timestamp": time.time(),
        }

        # Get container stats
        result = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", "json"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT, check=False,
        )

        if result.returncode == 0 and result.stdout.strip():
            container_stats = []
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    container_stats.append(json.loads(line))

            performance_data["containers"] = container_stats

        # Get system info
        system_result = subprocess.run(
            ["docker", "system", "df", "--format", "json"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT, check=False,
        )

        if system_result.returncode == 0 and system_result.stdout.strip():
            system_info = []
            for line in system_result.stdout.strip().split("\n"):
                if line.strip():
                    system_info.append(json.loads(line))

            performance_data["system"] = system_info

        return json.dumps(performance_data, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.tool()
def debug_docker_issues() -> str:
    """Debug common Docker issues and provide solutions.

    Returns
    -------
        JSON string with debugging information and solutions

    """
    try:
        debug_info = {
            "success": True,
            "issues": [],
            "solutions": [],
            "recommendations": [],
            "timestamp": time.time(),
        }

        # Check Docker daemon
        daemon_result = subprocess.run(
            ["docker", "version"], capture_output=True, text=True, cwd=PROJECT_ROOT, check=False,
        )

        if daemon_result.returncode != 0:
            debug_info["issues"].append("Docker daemon not running")
            debug_info["solutions"].append(
                "Start Docker daemon: sudo systemctl start docker",
            )

        # Check Docker Compose
        compose_result = subprocess.run(
            ["docker-compose", "version"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT, check=False,
        )

        if compose_result.returncode != 0:
            debug_info["issues"].append("Docker Compose not available")
            debug_info["solutions"].append(
                "Install Docker Compose: sudo apt-get install docker-compose",
            )

        # Check for port conflicts
        port_check = subprocess.run(
            ["netstat", "-tlnp"], capture_output=True, text=True, cwd=PROJECT_ROOT, check=False,
        )

        if port_check.returncode == 0:
            ports = ["8000", "5432", "6379", "5000"]
            for port in ports:
                if f":{port}" in port_check.stdout:
                    debug_info["issues"].append(f"Port {port} is in use")
                    debug_info["solutions"].append(
                        f"Free port {port} or change configuration",
                    )

        # Check disk space
        disk_result = subprocess.run(
            ["df", "-h"], capture_output=True, text=True, cwd=PROJECT_ROOT, check=False,
        )

        if disk_result.returncode == 0:
            for line in disk_result.stdout.split("\n"):
                if "/dev/" in line and "9" in line.split()[4]:  # 90%+ usage
                    debug_info["issues"].append("Disk space low")
                    debug_info["solutions"].append(
                        "Free up disk space: docker system prune -a",
                    )

        # Check Docker images
        images_result = subprocess.run(
            ["docker", "images"], capture_output=True, text=True, cwd=PROJECT_ROOT, check=False,
        )

        if images_result.returncode == 0:
            image_count = len(images_result.stdout.split("\n")) - 1
            if image_count > 10:
                debug_info["recommendations"].append(
                    "Consider cleaning up unused Docker images",
                )

        return json.dumps(debug_info, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=2)


@mcp.resource("docker://status")
def docker_status_resource() -> str:
    """Get current Docker status."""
    try:
        result = get_docker_status()
        data = json.loads(result)
        if data.get("success"):
            container_count = len(data.get("containers", []))
            return f"Docker Status: {container_count} containers running"
        else:
            return f"Docker Status: Error - {data.get('error', 'Unknown error')}"
    except Exception as e:
        return f"Error getting Docker status: {e!s}"


@mcp.resource("docker://health")
def docker_health_resource() -> str:
    """Get current Docker health status."""
    try:
        result = check_docker_health()
        data = json.loads(result)
        if data.get("success"):
            overall_health = data.get("overall_health", "unknown")
            return f"Docker Health: {overall_health}"
        else:
            return f"Docker Health: Error - {data.get('error', 'Unknown error')}"
    except Exception as e:
        return f"Error getting Docker health: {e!s}"


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
