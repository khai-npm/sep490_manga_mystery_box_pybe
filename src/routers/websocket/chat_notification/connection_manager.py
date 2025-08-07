from fastapi import WebSocket
from typing import Dict, List

active_connections: Dict[str, List[WebSocket]] = {}

async def connect(websocket: WebSocket, user_id: str):
    await websocket.accept()
    if  user_id not in active_connections:
        active_connections[ user_id] = []
    active_connections[user_id].append(websocket)

def disconnect(websocket: WebSocket, user_id: str):
    active_connections[user_id].remove(websocket)
    if not active_connections[user_id]:
        del active_connections[user_id]

async def broadcast(message: dict, user_id: str):
    for connection in active_connections.get(user_id, []):
        await connection.send_json(message)