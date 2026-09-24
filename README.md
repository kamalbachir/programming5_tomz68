# Cinema Ticket Booking (Programming 5)

A customer picks a movie showtime and books a seat. Staff manage movies,
showtimes and tickets. Every connected client sees a seat become taken
(or freed) **instantly**.

Python + FastAPI. Data is kept in memory (no database).

## Architecture

```
 [Customer client]                      [Staff client]
        \                                     /
         \-- HTTP ----->  API Gateway  <-----/            :8000
                          /     |      \
                         v      v       v
                    [Auth]  [Movie]  [Booking]            :8001 :8002 :8003
                                        |
                                        v
                                 [Notification]            :8004
                                  /            \
                    (WebSocket) v                v (WebSocket)
              [Customer client]              [Staff client]
```

Clients only talk HTTP to the **gateway** — never straight to a backend
service. The gateway forwards each request with `httpx` and hands the
answer back unchanged. The only exception is the WebSocket: both clients
connect to the notification service directly, because a gateway adds
nothing to a live push channel.

| Service | Port | Endpoints |
|---|---|---|
| gateway | 8000 | forwards everything below |
| auth_service | 8001 | `POST /login` (username only, no password) |
| movie_service | 8002 | `GET /movies`, `POST /movies`, `POST /movies/{id}/showtimes`, `GET /showtimes/{id}` |
| booking_service | 8003 | `POST /bookings`, `GET /bookings`, `DELETE /bookings/{id}` |
| notification_service | 8004 | `WS /ws`, `POST /notify` |

**API documentation:** FastAPI generates it automatically. With the services
running, open `http://localhost:8000/docs` (the gateway) or any service's
own `/docs` on its port.

## Booking flow

1. Customer logs in with just a username (client → gateway → auth).
2. Customer books a seat (client → gateway → booking).
3. Booking asks the movie service whether the showtime exists.
4. If the seat is already taken, booking returns **409 Conflict**.
5. Otherwise it saves the ticket and calls the notification service.
6. Notification pushes `{"event": "seat_taken", "seat": "C7", ...}` over
   WebSocket to every connected client — customer and staff alike.

## Clients

There are two kinds of client, on purpose: a CLI and a web page for each
role. Either pair is enough to demo the whole flow.

- `clients/cli/customer_client.py`, `clients/cli/staff_client.py` — terminal apps.
- `clients/web/customer.html`, `clients/web/staff.html` — plain HTML/CSS/JS,
  no framework, no build step. Minimal styling on purpose (`clients/web/styles.css`).

## Run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
./run_all.sh                                          # terminal 1: starts the 5 services
```

**CLI:**
```bash
.venv/bin/python clients/cli/customer_client.py        # terminal 2 (quick-login: 1 or 2)
.venv/bin/python clients/cli/staff_client.py           # terminal 3 (quick-login: 1 or 2)
```

**Web:**
```bash
cd clients/web && python3 -m http.server 8080          # then open:
# http://localhost:8080/customer.html
# http://localhost:8080/staff.html
```

Movie service starts pre-seeded with **Dune** (showtime 1 at 18:00, showtime 2
at 21:00) so there's something to book right away.

**CLI customer commands:** `movies`, `book <showtime_id> <seat>`, `quit`
**CLI staff commands:** `movies`, `addmovie <title>`, `addshowtime <movie_id> <time>`,
`tickets`, `cancel <ticket_id>`, `quit`

## Demo script (for the video)

1. Start the services. Show `http://localhost:8000/docs` (the gateway).
2. Serve the web clients and open `customer.html` and `staff.html` side by
   side. Click the **alice** quick-fill button on one, **staff1** on the
   other, and press Login on each.
3. Customer: type a seat (e.g. `C7`) on the 18:00 showtime and click **Book**.
   The ticket appears instantly in the staff page's Tickets and Live Activity
   — no refresh.
4. Staff: click **Cancel** on that ticket. The customer page shows
   "seat C7 freed" live.
5. Book the same seat twice from two browser tabs to show the **409
   Conflict** (the second click shows an inline error).
6. Optionally repeat the same flow with the CLI clients to show the second
   client type.

## Defense cheat-sheet

- **Why an API Gateway?** Clients only need to know one address. The gateway
  hides which service handles what, and services can move or change ports
  without the clients caring.
- **Why microservices?** Each service does one job (auth, movies, bookings,
  notifications) and can run, change or fail on its own.
- **How do they talk?** Over HTTP with `httpx`. The gateway forwards client
  requests; booking calls movie (to check a showtime) and notification (to
  push an update) directly — that's normal, a gateway is only for the
  client-facing side.
- **Where is real-time?** The notification service keeps a WebSocket open to
  every client. Booking POSTs an event to it, and it pushes that event to
  everyone connected — no polling, no refresh.
- **Why the 409 status code?** It's the correct HTTP meaning for "this
  conflicts with the current state" — exactly what a double seat booking is.
- **Why no database?** To keep the project simple. Each service holds its
  data in a Python dict. A real system would give each service its own
  database.
- **Known simplifications:** login is a plain username with no password,
  hashing or token; anyone can cancel any ticket; data resets on restart.
  These are acceptable for a course demo — say so before he asks.
