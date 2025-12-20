#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $FRONTEND_PID $BACKEND_PID 2>/dev/null
    exit
}

# Trap Ctrl+C (SIGINT) and call cleanup
trap cleanup SIGINT

# Start frontend
echo "Starting frontend on http://localhost:3000..."
cd frontend
npx http-server -p 3000 &
FRONTEND_PID=$!

# Wait until frontend is ready
echo "Waiting for frontend to be ready..."
while ! curl -s http://localhost:3000 >/dev/null; do
    sleep 1
done

# Open default web browser at localhost:3000
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:3000"
elif command -v open &> /dev/null; then
    open "http://localhost:3000"
elif command -v start &> /dev/null; then
    start "http://localhost:3000"
fi

# Activate backend virtual environment
cd ../backend
source .venv/bin/activate

# Start Django backend on port 8000
echo "Starting Django backend on http://localhost:8000..."
python manage.py runserver 8000 &
BACKEND_PID=$!

# Wait for both processes
wait $FRONTEND_PID $BACKEND_PID
