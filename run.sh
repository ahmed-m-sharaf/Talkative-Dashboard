#!/bin/bash

# Talkative Dashboard Runner Script
# Runs both the FastAPI backend and Streamlit frontend in one command

# Determine correct virtual environment path
ENV_PATH="/home/sharaf/enviroments/ai_latest"
if [ -d "$ENV_PATH" ]; then
    echo "[Info] Using Python environment from $ENV_PATH"
    PYTHON_BIN="$ENV_PATH/bin/python"
    STREAMLIT_BIN="$ENV_PATH/bin/streamlit"
else
    echo "[Warning] Environment $ENV_PATH not found, falling back to system defaults"
    PYTHON_BIN="python"
    STREAMLIT_BIN="streamlit"
fi

# Function to clean up background processes on exit
cleanup() {
    echo ""
    if [ -n "$API_PID" ]; then
        echo "[Info] Stopping FastAPI backend (PID: $API_PID)..."
        kill "$API_PID" 2>/dev/null
    fi
    echo "[Info] Cleanup complete. Exiting."
    exit 0
}

# Trap SIGINT (Ctrl+C), SIGTERM, and EXIT to run cleanup
trap cleanup SIGINT SIGTERM EXIT

# 1. Start FastAPI Backend in background
echo "[Info] Starting FastAPI Chatbot API on port 8005..."
$PYTHON_BIN -m uvicorn api:app --port 8005 --host 127.0.0.1 > /dev/null 2>&1 &
API_PID=$!

# Wait briefly for FastAPI to initialize
sleep 2

# Check if the backend started successfully
if kill -0 "$API_PID" 2>/dev/null; then
    echo "[Info] FastAPI backend successfully started (PID: $API_PID)."
else
    echo "[Error] Failed to start FastAPI backend. Exiting."
    exit 1
fi

# 2. Start Streamlit Frontend in foreground
echo "[Info] Starting Streamlit App..."
$STREAMLIT_BIN run app.py
