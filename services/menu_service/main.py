from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Menu Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

menu = {
    1: {"id": 1, "name": "Burger", "price": 5},
    2: {"id": 2, "name": "Pizza", "price": 4},
    3: {"id": 3, "name": "Salad", "price": 3},
    4: {"id": 4, "name": "Coffee", "price": 2},
}


@app.get("/menu")
def list_menu():
    return list(menu.values())


@app.get("/menu/{item_id}")
def get_item(item_id: int):
    if item_id not in menu:
        raise HTTPException(404, "item not found")
    return menu[item_id]
