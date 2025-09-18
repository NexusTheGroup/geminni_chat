#!/bin/bash
# Start Build Debug MCP Server for NexusKnowledge

set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment
source "$PROJECT_ROOT/.venv/bin/activate"

# Change to project directory
cd "$PROJECT_ROOT"

echo "Starting NexusKnowledge Build Debug MCP Server..."
echo "Project root: $PROJECT_ROOT"
echo "Virtual environment: $PROJECT_ROOT/.venv"

# Start the build debug MCP server
python "$PROJECT_ROOT/src/nexus_knowledge/mcp/build_debug_server.py"
