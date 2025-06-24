from fastapi import WebSocket
from typing import Dict, List

active_connections: Dict[str, List[WebSocket]] = {}

async def connect(websocket: WebSocket, conversation_id: str):
    await websocket.accept()
    if conversation_id not in active_connections:
        active_connections[conversation_id] = []
    active_connections[conversation_id].append(websocket)

def disconnect(websocket: WebSocket, conversation_id: str):
    active_connections[conversation_id].remove(websocket)
    if not active_connections[conversation_id]:
        del active_connections[conversation_id]

async def broadcast(message: dict, conversation_id: str):
    for connection in active_connections.get(conversation_id, []):
        await connection.send_json(message)