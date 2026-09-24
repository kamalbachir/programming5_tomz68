from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Auth Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class Login(BaseModel):
    username: str


@app.post("/login")
def login(l: Login):
    # No password: whoever gives a username is logged in. This is a course
    # demo, not a real system, so we skip hashing, tokens and JWT on purpose.
    return {"username": l.username}
