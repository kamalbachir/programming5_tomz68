from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Notification Service (WebSocket)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

clients = []  # every connected client (customer or staff)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
    try:
        while True:
            await ws.receive_text()  # keep the connection open
    except WebSocketDisconnect:
        clients.remove(ws)


@app.post("/notify")
async def notify(event: dict):
    """Called by the booking service over HTTP. We push the event to all clients."""
    for ws in list(clients):
        try:
            await ws.send_json(event)
        except Exception:
            clients.remove(ws)
    return {"sent_to": len(clients)}
