from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Movie Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

movies = {}      # movie_id -> {id, title}
showtimes = {}   # showtime_id -> {id, movie_id, movie_title, time}
next_movie_id = 1
next_showtime_id = 1


def seed():
    """A couple of movies so the demo has something to show right away."""
    global next_movie_id, next_showtime_id
    movies[1] = {"id": 1, "title": "Dune"}
    showtimes[1] = {"id": 1, "movie_id": 1, "movie_title": "Dune", "time": "18:00"}
    showtimes[2] = {"id": 2, "movie_id": 1, "movie_title": "Dune", "time": "21:00"}
    next_movie_id, next_showtime_id = 2, 3


seed()


class NewMovie(BaseModel):
    title: str


class NewShowtime(BaseModel):
    time: str


@app.get("/movies")
def list_movies():
    return [
        {**m, "showtimes": [s for s in showtimes.values() if s["movie_id"] == m["id"]]}
        for m in movies.values()
    ]


@app.post("/movies")
def add_movie(m: NewMovie):
    global next_movie_id
    movie = {"id": next_movie_id, "title": m.title}
    movies[movie["id"]] = movie
    next_movie_id += 1
    return movie


@app.post("/movies/{movie_id}/showtimes")
def add_showtime(movie_id: int, s: NewShowtime):
    global next_showtime_id
    if movie_id not in movies:
        raise HTTPException(404, "movie not found")
    showtime = {"id": next_showtime_id, "movie_id": movie_id,
                "movie_title": movies[movie_id]["title"], "time": s.time}
    showtimes[showtime["id"]] = showtime
    next_showtime_id += 1
    return showtime


@app.get("/showtimes/{showtime_id}")
def get_showtime(showtime_id: int):
    if showtime_id not in showtimes:
        raise HTTPException(404, "showtime not found")
    return showtimes[showtime_id]
