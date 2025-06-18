#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Function to cleanup background processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $FLASK_PID $FASTAPI_PID $CAMERA_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

echo "Starting Fatigue Detection System..."

# Start FastAPI server (fatigue detection) in background
echo "Starting FastAPI server (fatigue detection) on port 8000..."
python fatigue_server.py &
FASTAPI_PID=$!

# Wait a moment for FastAPI to start
sleep 3

# Start Flask server (main application) in background
echo "Starting Flask server (main app) on port 5000..."
python app.py --obd mock --debug --host 0.0.0.0 --port 5000 &
FLASK_PID=$!

# Wait a moment for Flask to start
sleep 3

# Start camera capture in background
echo "Starting camera capture..."
python camera_capture.py &
CAMERA_PID=$!

echo "All services started!"
echo "FastAPI (fatigue detection): http://localhost:8000"
echo "Flask (main app): http://localhost:5000"
echo "Camera capture: Running in background"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for all processes
wait $FASTAPI_PID $FLASK_PID $CAMERA_PID 