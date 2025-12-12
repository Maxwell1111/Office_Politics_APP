#!/bin/bash
# Test the minimal app locally to ensure it works

echo "Installing dependencies..."
pip3 install -q fastapi==0.104.1 uvicorn==0.24.0

echo "Starting server on port 8888..."
PORT=8888 uvicorn app_minimal:app --host 0.0.0.0 --port 8888 &
PID=$!

echo "Waiting for server to start..."
sleep 3

echo "Testing endpoints..."
curl -s http://localhost:8888/ | python3 -m json.tool
echo ""
curl -s http://localhost:8888/health | python3 -m json.tool

echo "Killing server..."
kill $PID

echo "Test complete!"
