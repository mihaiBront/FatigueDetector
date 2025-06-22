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

echo "🔍 Verificando estado del sistema antes de iniciar..."

# Check if camera diagnostic script exists
if [ -f "check_cameras.py" ]; then
    echo "📷 Ejecutando diagnóstico de cámaras..."
    python check_cameras.py
    echo ""
    echo "¿Continuar con el inicio del sistema? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Inicio cancelado por el usuario"
        exit 0
    fi
else
    echo "⚠️  Script de diagnóstico de cámaras no encontrado"
fi

echo ""
echo "🚀 Starting Fatigue Detection System with Real Bluetooth Data..."

# Start FastAPI server (fatigue detection) in background
echo "Starting FastAPI server (fatigue detection) on port 8000..."
python fatigue_server.py &
FASTAPI_PID=$!

# Wait a moment for FastAPI to start
sleep 3

# Start Flask server (main application) in background with real Bluetooth
echo "Starting Flask server (main app) on port 5000 with real Bluetooth data..."
python app.py --obd esp32 --debug --host 0.0.0.0 --port 5000 &
FLASK_PID=$!

# Wait a moment for Flask to start
sleep 3

# Start camera capture in background
echo "Starting camera capture (detección automática)..."
python camera_capture.py &
CAMERA_PID=$!

echo ""
echo "✅ All services started!"
echo "FastAPI (fatigue detection): http://localhost:8000"
echo "Flask (main app): http://localhost:5000"
echo "Camera capture: Running in background with auto-detection"
echo "Bluetooth: Connected to real OBD device (ESP32)"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for all processes
wait $FLASK_PID $FASTAPI_PID $CAMERA_PID 