#!/bin/bash
# Start GitHub MCP Server for NexusKnowledge

set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment
source "$PROJECT_ROOT/.venv/bin/activate"

# Change to project directory
cd "$PROJECT_ROOT"

# Check for GitHub credentials
if [ -z "$GITHUB_PAT_KEY" ]; then
    echo "Warning: GITHUB_PAT_KEY environment variable not set"
    echo "Some GitHub features may not work properly"
fi

if [ -z "$GITHUB_USERNAME" ]; then
    echo "Warning: GITHUB_USERNAME environment variable not set"
    echo "Some GitHub features may not work properly"
fi

echo "Starting NexusKnowledge GitHub MCP Server..."
echo "Project root: $PROJECT_ROOT"
echo "Virtual environment: $PROJECT_ROOT/.venv"

# Start the GitHub MCP server
python "$PROJECT_ROOT/src/nexus_knowledge/mcp/github_server.py"
