import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

MOVIE_URL = "http://localhost:8002"
NOTIFY_URL = "http://localhost:8004"

app = FastAPI(title="Booking Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

tickets = {}  # ticket_id -> {id, username, showtime_id, seat}
next_ticket_id = 1


class NewBooking(BaseModel):
    username: str
    showtime_id: int
    seat: str


def seat_is_taken(showtime_id, seat):
    return any(t["showtime_id"] == showtime_id and t["seat"] == seat for t in tickets.values())


@app.post("/bookings")
async def book_seat(b: NewBooking):
    global next_ticket_id
    async with httpx.AsyncClient() as http:
        # 1. does the showtime exist? (movie service)
        if (await http.get(f"{MOVIE_URL}/showtimes/{b.showtime_id}")).status_code != 200:
            raise HTTPException(404, "showtime not found")
        # 2. is the seat free?
        if seat_is_taken(b.showtime_id, b.seat):
            raise HTTPException(409, "seat already taken")
        # 3. save the ticket and tell everyone (notification service)
        ticket = {"id": next_ticket_id, "username": b.username,
                  "showtime_id": b.showtime_id, "seat": b.seat}
        tickets[ticket["id"]] = ticket
        next_ticket_id += 1
        await http.post(f"{NOTIFY_URL}/notify", json={
            "event": "seat_taken", "showtime_id": b.showtime_id, "seat": b.seat, "ticket": ticket,
        })
        return ticket


@app.get("/bookings")
def list_bookings():
    return list(tickets.values())


@app.delete("/bookings/{ticket_id}")
async def cancel_booking(ticket_id: int):
    if ticket_id not in tickets:
        raise HTTPException(404, "ticket not found")
    ticket = tickets.pop(ticket_id)
    async with httpx.AsyncClient() as http:
        await http.post(f"{NOTIFY_URL}/notify", json={
            "event": "seat_freed", "showtime_id": ticket["showtime_id"], "seat": ticket["seat"],
        })
    return {"cancelled": ticket_id}
