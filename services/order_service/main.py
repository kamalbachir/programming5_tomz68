import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

USER_URL = "http://localhost:8001"
MENU_URL = "http://localhost:8002"
PAYMENT_URL = "http://localhost:8004"
NOTIFY_URL = "http://localhost:8005"

app = FastAPI(title="Order Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

orders = {}  # id -> order (in memory)


class NewOrder(BaseModel):
    user: str
    item_id: int


async def notify(http, event, order):
    await http.post(f"{NOTIFY_URL}/notify", json={"event": event, "order": order})


@app.post("/orders")
async def create_order(new: NewOrder):
    async with httpx.AsyncClient() as http:
        # 1. does the user exist? (user service)
        if (await http.get(f"{USER_URL}/users/{new.user}")).status_code != 200:
            raise HTTPException(404, "unknown user")
        # 2. what does the item cost? (menu service)
        r = await http.get(f"{MENU_URL}/menu/{new.item_id}")
        if r.status_code != 200:
            raise HTTPException(404, "unknown item")
        item = r.json()
        # 3. pay (payment service)
        await http.post(f"{PAYMENT_URL}/pay", json={"user": new.user, "amount": item["price"]})
        # 4. save the order and tell everyone (notification service)
        order = {"id": len(orders) + 1, "user": new.user, "item": item["name"],
                 "price": item["price"], "status": "preparing"}
        orders[order["id"]] = order
        await notify(http, "new_order", order)
        return order


@app.get("/orders")
def list_orders():
    return list(orders.values())


@app.post("/orders/{order_id}/ready")
async def mark_ready(order_id: int):
    if order_id not in orders:
        raise HTTPException(404, "order not found")
    orders[order_id]["status"] = "ready"
    async with httpx.AsyncClient() as http:
        await notify(http, "order_ready", orders[order_id])
    return orders[order_id]
