#!/bin/bash
# Script to set up and switch Python environments for IoT Risk Dashboard
# Usage: ./setup_python.sh [3.10|3.12]

# Default to Python 3.12 if no version is specified
PYTHON_VERSION=${1:-3.12}

if [ "$PYTHON_VERSION" != "3.10" ] && [ "$PYTHON_VERSION" != "3.12" ]; then
    echo "Error: Unsupported Python version specified."
    echo "Usage: ./setup_python.sh [3.10|3.12]"
    exit 1
fi

ENV_DIR="venv$PYTHON_VERSION"

# Check if virtual environment exists, if not create it
if [ ! -d "$ENV_DIR" ]; then
    echo "Creating Python $PYTHON_VERSION virtual environment..."
    python$PYTHON_VERSION -m venv "$ENV_DIR"
fi

# Activate the virtual environment
echo "Activating Python $PYTHON_VERSION environment..."
source "$ENV_DIR/bin/activate"

# Upgrade pip and install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Print Python version information
python_version=$(python --version)
echo "Successfully set up $python_version environment."
echo ""
echo "To use this environment, run:"
echo "source $ENV_DIR/bin/activate"
echo ""
echo "To exit this environment, run:"
echo "deactivate"
