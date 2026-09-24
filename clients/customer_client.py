import json
import threading

import requests
from websockets.sync.client import connect

GATEWAY = "http://localhost:8000"
NOTIFY = "ws://localhost:8004/ws"


def listen():
    """Runs in the background and prints every live seat update."""
    with connect(NOTIFY) as ws:
        for message in ws:
            e = json.loads(message)
            if e["event"] == "seat_taken":
                print(f"\n[LIVE] seat {e['seat']} just got booked (showtime {e['showtime_id']})")
            elif e["event"] == "seat_freed":
                print(f"\n[LIVE] seat {e['seat']} is free again (showtime {e['showtime_id']})")


# quick login: pick a demo user, or type your own (no password needed)
choice = input("Quick login: 1) alice  2) bob  (or press Enter to type your own): ")
username = ["alice", "bob"][int(choice) - 1] if choice in ("1", "2") else input("username: ")
requests.post(f"{GATEWAY}/login", json={"username": username})
print(f"Logged in as {username}")

threading.Thread(target=listen, daemon=True).start()
print("Commands: movies | book <showtime_id> <seat> | quit")

while True:
    cmd = input("> ").split()
    if not cmd:
        continue
    if cmd[0] == "movies":
        for m in requests.get(f"{GATEWAY}/movies").json():
            print(f"  [{m['id']}] {m['title']}")
            for s in m["showtimes"]:
                print(f"      showtime {s['id']}: {s['time']}")
    elif cmd[0] == "book" and len(cmd) == 3:
        r = requests.post(f"{GATEWAY}/bookings",
                           json={"username": username, "showtime_id": int(cmd[1]), "seat": cmd[2]})
        print(r.status_code, r.json())
    elif cmd[0] == "quit":
        break
    else:
        print("unknown command")
