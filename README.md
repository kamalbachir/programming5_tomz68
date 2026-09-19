# Cafeteria Ordering (Programming 5)

A customer orders food. Every client sees the order **live** and can mark it ready.

Python + FastAPI. Data is kept in memory (no database).

## Architecture

```
 CLI client ──┐                                   ┌── user_service          :8001  (register / login)
              ├── HTTP ──> order_service :8003 ───┼── menu_service          :8002  (menu + prices)
 Web client ──┘                  │                └── payment_service       :8004  (fake payment)
      ▲                          │ HTTP POST /notify
      │  WebSocket               ▼
      └──────────────── notification_service :8005  (pushes live events)
```

| Service | Port | Endpoints |
|---|---|---|
| user_service | 8001 | `POST /register`, `POST /login`, `GET /users/{name}` |
| menu_service | 8002 | `GET /menu`, `GET /menu/{id}` |
| order_service | 8003 | `POST /orders`, `GET /orders`, `POST /orders/{id}/ready` |
| payment_service | 8004 | `POST /pay`, `GET /payments` |
| notification_service | 8005 | `WS /ws`, `POST /notify` |

**API documentation:** FastAPI generates it automatically. With the services running, open
`http://localhost:8001/docs` (change the port for each service).

## Run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
./run_all.sh                              # terminal 1: starts the 5 services
```

```bash
.venv/bin/python clients/cli/cli.py       # terminal 2: CLI client (press 1 or 2 to quick-login)
```

```bash
cd clients/web && python3 -m http.server 8080   # terminal 3, then open http://localhost:8080
```

## Demo script (for the video)

1. Start the services. Show `http://localhost:8003/docs`.
2. Open the web client (click the **alice** quick-fill button, then Login) and the CLI (press `2` to log in as bob) side by side.
3. In the CLI: `menu`, then `order 1`. The order **appears live in the browser**.
4. In the browser: click **Mark ready**. The CLI prints `[LIVE] order_ready ...`.

## Defense cheat-sheet

- **Why microservices?** Each service does one job and can run, change or fail on its own.
- **How do they talk?** Over HTTP. `order_service` calls user, menu and payment, then notification.
- **Where is real-time?** `notification_service` keeps a WebSocket open to every client. When
  `order_service` POSTs `/notify`, it pushes the event to all connected clients.
- **Why no database?** To keep the project simple. Each service holds its data in a Python dict/list.
  A real system would give each service its own database.
- **Why FastAPI?** Very little code, built-in WebSocket support, automatic API docs.
- **Known simplifications:** passwords are stored in plain text, and there are no tokens. Anyone can
  mark an order ready. This is acceptable for a course demo, but say so before he asks.
