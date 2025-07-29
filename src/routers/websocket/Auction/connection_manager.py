from fastapi import WebSocket
from typing import Dict, List

active_connections: Dict[str, List[WebSocket]] = {}

async def connect(websocket: WebSocket, auction_id: str):
    await websocket.accept()
    if  auction_id not in active_connections:
        active_connections[ auction_id] = []
    active_connections[auction_id].append(websocket)

def disconnect(websocket: WebSocket, auction_id: str):
    active_connections[auction_id].remove(websocket)
    if not active_connections[auction_id]:
        del active_connections[auction_id]

async def broadcast(message: dict, auction_id: str):
    for connection in active_connections.get(auction_id, []):
        await connection.send_json(message)