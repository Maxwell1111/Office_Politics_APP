#!/bin/bash
# ABSOLUTE MINIMUM BUILD - Just 2 packages
set -e
echo "Installing FastAPI and Uvicorn only..."
pip install --no-cache-dir fastapi==0.104.1 uvicorn==0.24.0
echo "Build complete!"
