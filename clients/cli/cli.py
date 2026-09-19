import json
import threading

import httpx
from websockets.sync.client import connect

USER, MENU, ORDER, NOTIFY = "localhost:8001", "localhost:8002", "localhost:8003", "localhost:8005"


def listen():
    """Runs in the background and prints every live event from the WebSocket."""
    with connect(f"ws://{NOTIFY}/ws") as ws:
        for message in ws:
            e = json.loads(message)
            o = e["order"]
            print(f"\n[LIVE] {e['event']}: order #{o['id']} {o['item']} ({o['user']}) -> {o['status']}")


# login
choice = input("Quick login: 1) alice  2) bob  (or press Enter to type your own): ")
if choice in ("1", "2"):
    name, password = ["alice", "bob"][int(choice) - 1], "1234"  # demo shortcut
else:
    name = input("name: ")
    password = input("password: ")
if httpx.post(f"http://{USER}/login", json={"name": name, "password": password}).status_code != 200:
    raise SystemExit("login failed")

threading.Thread(target=listen, daemon=True).start()
print("Commands: menu | order <item_id> | ready <order_id> | orders | quit")

while True:
    cmd = input("> ").split()
    if not cmd:
        continue
    if cmd[0] == "menu":
        for i in httpx.get(f"http://{MENU}/menu").json():
            print(f"  {i['id']}. {i['name']} - ${i['price']}")
    elif cmd[0] == "order" and len(cmd) == 2:
        r = httpx.post(f"http://{ORDER}/orders", json={"user": name, "item_id": int(cmd[1])})
        print(r.json())
    elif cmd[0] == "ready" and len(cmd) == 2:
        print(httpx.post(f"http://{ORDER}/orders/{cmd[1]}/ready").json())
    elif cmd[0] == "orders":
        for o in httpx.get(f"http://{ORDER}/orders").json():
            print(f"  #{o['id']} {o['item']} ({o['user']}) - {o['status']}")
    elif cmd[0] == "quit":
        break
