#!/bin/bash
# Render.com optimized build script
# Limits memory usage during npm build

set -e  # Exit on error

echo "🚀 Starting Render.com build..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --no-cache-dir --upgrade pip
pip install --no-cache-dir -r requirements.txt
pip install --no-cache-dir -e .

# Build frontend with memory constraints
echo "🎨 Building frontend (with memory optimization)..."
cd www

# Clear any existing dist
rm -rf dist

# Install npm dependencies with limited concurrency
echo "📦 Installing npm dependencies (limited concurrency)..."
npm install --prefer-offline --no-audit --progress=false

# Set Node memory limit to 400MB (Render free tier has 512MB total)
export NODE_OPTIONS="--max-old-space-size=400"

# Build with webpack
echo "🔨 Running webpack build..."
npm run build

cd ..

echo "✅ Build completed successfully!"
