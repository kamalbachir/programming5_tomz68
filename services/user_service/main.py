from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="User Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

users = {"alice": "1234", "bob": "1234"}  # name -> password (in memory)


class Credentials(BaseModel):
    name: str
    password: str


@app.post("/register")
def register(c: Credentials):
    if c.name in users:
        raise HTTPException(400, "user already exists")
    users[c.name] = c.password
    return {"name": c.name}


@app.post("/login")
def login(c: Credentials):
    if users.get(c.name) != c.password:
        raise HTTPException(401, "wrong name or password")
    return {"name": c.name}


@app.get("/users/{name}")
def get_user(name: str):
    if name not in users:
        raise HTTPException(404, "user not found")
    return {"name": name}
