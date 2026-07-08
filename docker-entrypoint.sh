#!/bin/bash
set -e

# If database doesn't exist, initialize and seed it
if [ ! -f "recruitment.db" ]; then
    echo "Database not found. Initializing..."
    python init_db.py
    echo "Seeding database..."
    python -m database.seed
fi

# Start FastAPI backend
echo "Starting FastAPI Chatbot API on port 8005..."
uvicorn api:app --host 0.0.0.0 --port 8005 &
API_PID=$!

# Start Streamlit frontend
echo "Starting Streamlit frontend on port 8501..."
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
STREAMLIT_PID=$!

# Handle exit/termination signals to stop child processes gracefully
cleanup() {
    echo "Stopping all services..."
    kill -TERM "$API_PID" 2>/dev/null
    kill -TERM "$STREAMLIT_PID" 2>/dev/null
    wait "$API_PID" "$STREAMLIT_PID" 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for either process to exit
wait -n

# Exit with status of the process that exited first
exit $?
