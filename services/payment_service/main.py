from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Payment Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

payments = []  # in memory


class Payment(BaseModel):
    user: str
    amount: int


@app.post("/pay")
def pay(p: Payment):
    if p.amount <= 0:
        raise HTTPException(400, "amount must be positive")
    payment = {"id": len(payments) + 1, "user": p.user, "amount": p.amount, "status": "paid"}
    payments.append(payment)  # fake payment: always succeeds
    return payment


@app.get("/payments")
def list_payments():
    return payments
