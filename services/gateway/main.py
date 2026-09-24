import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

AUTH_URL = "http://localhost:8001"
MOVIE_URL = "http://localhost:8002"
BOOKING_URL = "http://localhost:8003"

app = FastAPI(title="API Gateway")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# The gateway is the single door the clients knock on. Every route below just
# forwards the request to the right service and hands back its response.


async def forward(method: str, url: str, request: Request):
    body = await request.body()
    async with httpx.AsyncClient() as http:
        r = await http.request(method, url, content=body, headers={"Content-Type": "application/json"})
        return Response(r.content, status_code=r.status_code, media_type="application/json")


@app.post("/login")
async def login(request: Request):
    return await forward("POST", f"{AUTH_URL}/login", request)


@app.get("/movies")
async def list_movies():
    async with httpx.AsyncClient() as http:
        r = await http.get(f"{MOVIE_URL}/movies")
        return Response(r.content, status_code=r.status_code, media_type="application/json")


@app.post("/movies")
async def add_movie(request: Request):
    return await forward("POST", f"{MOVIE_URL}/movies", request)


@app.post("/movies/{movie_id}/showtimes")
async def add_showtime(movie_id: int, request: Request):
    return await forward("POST", f"{MOVIE_URL}/movies/{movie_id}/showtimes", request)


@app.post("/bookings")
async def book(request: Request):
    return await forward("POST", f"{BOOKING_URL}/bookings", request)


@app.get("/bookings")
async def bookings():
    async with httpx.AsyncClient() as http:
        r = await http.get(f"{BOOKING_URL}/bookings")
        return Response(r.content, status_code=r.status_code, media_type="application/json")


@app.delete("/bookings/{ticket_id}")
async def cancel(ticket_id: int):
    async with httpx.AsyncClient() as http:
        r = await http.delete(f"{BOOKING_URL}/bookings/{ticket_id}")
        return Response(r.content, status_code=r.status_code, media_type="application/json")
