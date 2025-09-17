#!/bin/bash
set -e

echo "🚀 Starting environment setup..."

# Install pip if not available
sudo apt-get update && sudo apt-get install -y python3-pip

# Create and activate virtual environment
echo "📦 Creating Python virtual environment..."
python3.11 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install pre-commit mlflow "dvc[all]"

# Install pre-commit hooks
pre-commit install

# Install pnpm if not found
if ! command -v pnpm &> /dev/null; then
    echo "pnpm not found, installing..."
    npm install -g pnpm
fi

# Install Node.js dependencies
pnpm install

# Initialize DVC if not already done
if [ ! -d ".dvc" ]; then
    echo "Initializing DVC..."
    dvc init --no-scm
fi

# Make scripts executable
chmod +x scripts/*.sh

echo "✅ Environment setup complete."
