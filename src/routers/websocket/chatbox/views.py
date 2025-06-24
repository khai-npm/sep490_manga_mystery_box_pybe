from fastapi import APIRouter, Depends, FastAPI, WebSocket, WebSocketDisconnect
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from src.libs.jwt_authenication_handler import jwt_validator
from src.routers.websocket.chatbox.connection_manager import connect, disconnect, broadcast
from src.routers.websocket.chatbox.utils import websocket_util_verify_user
from src.models.User import User
from src.models.Conversations import Conversations
from src.models.Messages import Messages
import json

websocket_chatbox = APIRouter(prefix="/websocket", tags=["Websocket Chatbox"])
@websocket_chatbox.websocket("/chatbox/{conversation_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str, user_id: str):
    if await websocket_util_verify_user(websocket, user_id, conversation_id) is False:
        return
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
    except WebSocketDisconnect:
        disconnect(websocket, conversation_id)