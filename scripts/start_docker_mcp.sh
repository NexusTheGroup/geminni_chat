#!/bin/bash
# Start Docker MCP Server for NexusKnowledge

set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment
source "$PROJECT_ROOT/.venv/bin/activate"

# Change to project directory
cd "$PROJECT_ROOT"

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed or not in PATH"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "Error: Docker daemon is not running"
    echo "Please start Docker daemon: sudo systemctl start docker"
    exit 1
fi

echo "Starting NexusKnowledge Docker MCP Server..."
echo "Project root: $PROJECT_ROOT"
echo "Virtual environment: $PROJECT_ROOT/.venv"
echo "Docker version: $(docker --version)"
echo "Docker Compose version: $(docker-compose --version)"

# Start the Docker MCP server
python "$PROJECT_ROOT/src/nexus_knowledge/mcp/docker_server.py"
