from fastapi import APIRouter, Depends, FastAPI, WebSocket, WebSocketDisconnect
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from src.libs.jwt_authenication_handler import jwt_validator
from src.routers.websocket.chatbox.connection_manager import connect, disconnect, broadcast
from src.routers.websocket.chatbox.utils import websocket_util_verify_user, get_target_user_id
from src.models.User import User
from src.models.Conversations import Conversations
from src.models.Messages import Messages
from src.routers.websocket.chat_notification.connection_manager import broadcast as notifi_broadcast
import json

websocket_chatbox = APIRouter(prefix="/websocket", tags=["Websocket Chatbox"])
@websocket_chatbox.websocket("/chatbox/{conversation_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str, user_id: str):
    if await websocket_util_verify_user(websocket, user_id, conversation_id) is False:
        return
    target_user_id = await get_target_user_id(user_id, conversation_id)
    await connect(websocket, conversation_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data : Messages = Messages(
                content=data,
                sender_id=user_id,
                created_at=datetime.now(),
                conversation_id=conversation_id

            )

            message_data_json = {
                "content" : message_data.content,
                "sender_id" : message_data.sender_id,
                "created_at" : str(message_data.created_at.strftime("%H:%M")),
                "conversation_id" : message_data.conversation_id

            }

            await message_data.insert()
            await broadcast(message_data_json, conversation_id)
            message_notification = {
                "sender_id" : message_data.sender_id,
                "sent_at" : str(datetime.now().strftime("%H:%M"))
            }
            await notifi_broadcast(message_notification, target_user_id)
    except WebSocketDisconnect:
        disconnect(websocket, conversation_id)