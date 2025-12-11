#!/bin/bash
# Ultra-simple build for Render.com free tier
# No frontend, no complex dependencies

set -e

echo "🚀 Building Subtext Minimal MVP..."

# Install minimal Python dependencies
echo "📦 Installing dependencies..."
pip install --no-cache-dir -r requirements-minimal.txt

echo "✅ Build complete!"
echo "Ready to run: uvicorn app_simple:app --host 0.0.0.0 --port \$PORT"
