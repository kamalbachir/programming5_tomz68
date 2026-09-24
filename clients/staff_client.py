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
            print(f"\n[LIVE] {e['event']}: showtime {e['showtime_id']} seat {e['seat']}")


choice = input("Quick login: 1) staff1  2) staff2  (or press Enter to type your own): ")
username = ["staff1", "staff2"][int(choice) - 1] if choice in ("1", "2") else input("username: ")
requests.post(f"{GATEWAY}/login", json={"username": username})
print(f"Logged in as {username} (staff)")

threading.Thread(target=listen, daemon=True).start()
print("Commands: movies | addmovie <title> | addshowtime <movie_id> <time> | "
      "tickets | cancel <ticket_id> | quit")

while True:
    raw = input("> ").strip()
    if not raw:
        continue
    parts = raw.split(maxsplit=1)
    cmd, rest = parts[0], (parts[1] if len(parts) > 1 else "")

    if cmd == "movies":
        for m in requests.get(f"{GATEWAY}/movies").json():
            print(f"  [{m['id']}] {m['title']}")
            for s in m["showtimes"]:
                print(f"      showtime {s['id']}: {s['time']}")
    elif cmd == "addmovie" and rest:
        print(requests.post(f"{GATEWAY}/movies", json={"title": rest}).json())
    elif cmd == "addshowtime" and rest:
        movie_id, time = rest.split(maxsplit=1)
        print(requests.post(f"{GATEWAY}/movies/{movie_id}/showtimes", json={"time": time}).json())
    elif cmd == "tickets":
        for t in requests.get(f"{GATEWAY}/bookings").json():
            print(f"  #{t['id']} {t['username']} - showtime {t['showtime_id']} seat {t['seat']}")
    elif cmd == "cancel" and rest:
        print(requests.delete(f"{GATEWAY}/bookings/{rest}").json())
    elif cmd == "quit":
        break
    else:
        print("unknown command")
