#!/bin/bash
# Run IoT Risk Dashboard with Python 3.12

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Activate Python 3.12 environment
source venv312/bin/activate

# Run the application
echo "Starting IoT Risk Dashboard with $(python --version)"
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
