from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from store import FleetStore

app = FastAPI(title="Fleet Tracker")
store = FleetStore()


@app.api_route("/ram", methods=["GET", "HEAD"])
def get_ram() -> dict:
    return store.get_all()


@app.get("/reset")
def reset_ram() -> dict:
    store.reset()
    return {"ok": True}


@app.api_route("/", methods=["GET", "HEAD"])
def index() -> dict:
    return {"status": "Ok"}


@app.websocket("/ws")
async def ws(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            msg = await websocket.receive_json()
            action = msg.get("action")
            identifier = msg.get("identifier")

            if action == "store_gps":
                gps = msg.get("gps", {})
                store.store_gps(identifier, gps["lat"], gps["lng"], msg["time"])
                await websocket.send_json({"ok": True})
            elif action == "get_gps":
                result = store.get_gps(identifier)
                await websocket.send_json(result or {"error": "not found"})
            elif action == "get_speed":
                result = store.get_speed(identifier)
                await websocket.send_json(result or {"error": "not found"})
            elif action == "get_acceleration":
                result = store.get_acceleration(identifier)
                await websocket.send_json(result or {"error": "not found"})
            elif action == "get_telemetry":
                result = store.get_telemetry(identifier)
                await websocket.send_json(result or {"error": "not found"})
            else:
                await websocket.send_json({"error": "unknown action"})
    except WebSocketDisconnect:
        pass
