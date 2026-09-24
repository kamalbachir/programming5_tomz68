#!/bin/bash
# Starts all 5 microservices. Press Ctrl+C to stop them all.
cd "$(dirname "$0")"
PY=.venv/bin/python

trap 'kill 0' EXIT

start() {  # start <folder> <port>
  (cd services/$1 && ../../$PY -m uvicorn main:app --port $2) &
}

start gateway 8000
start auth_service 8001
start movie_service 8002
start booking_service 8003
start notification_service 8004

echo "All services running. Gateway: http://localhost:8000/docs"
wait
