from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.routers.websocket.chat_notification.connection_manager import broadcast,connect,disconnect


websocket_chat_notification = APIRouter(prefix="/websocket/chat-notification", tags=["Websocket Chat Notification"])

@websocket_chat_notification.websocket("/{user_id}")
async def chat_notification_websocket_endpoint(websocket: WebSocket, user_id : str):
    await connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            await broadcast(data, user_id)
    except WebSocketDisconnect:
        disconnect(websocket, user_id)