#!/bin/bash
# Render.com API-ONLY build (no frontend build)
# Use this for free tier to avoid memory issues

set -e  # Exit on error

echo "🚀 Starting Render.com API-ONLY build..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --no-cache-dir --upgrade pip
pip install --no-cache-dir -r requirements.txt
pip install --no-cache-dir -e .

# Create minimal dist directory (frontend not built)
echo "📁 Creating placeholder frontend directory..."
mkdir -p www/dist
echo '<!DOCTYPE html><html><head><title>Subtext API</title></head><body><h1>Subtext API Server</h1><p>API docs: <a href="/api">/api</a></p><p>Health check: <a href="/api/health">/api/health</a></p></body></html>' > www/dist/index.html

echo "✅ API-only build completed successfully!"
echo "ℹ️  Note: Frontend not built. Deploy frontend separately (Vercel/Netlify)"
