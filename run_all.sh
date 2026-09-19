#!/bin/bash
# Starts all 5 microservices. Press Ctrl+C to stop them all.
cd "$(dirname "$0")"
PY=.venv/bin/python

trap 'kill 0' EXIT

start() {  # start <folder> <port>
  (cd services/$1 && ../../$PY -m uvicorn main:app --port $2) &
}

start user_service 8001
start menu_service 8002
start order_service 8003
start payment_service 8004
start notification_service 8005

echo "All services running. API docs: http://localhost:8001/docs ... 8005/docs"
wait
