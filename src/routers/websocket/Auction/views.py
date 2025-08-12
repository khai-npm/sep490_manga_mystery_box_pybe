from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.routers.websocket.Auction.utils import websocket_auction_util_verify_user
from src.routers.websocket.Auction.connection_manager import broadcast,connect,disconnect


websocket_auction = APIRouter(prefix="/websocket/auction", tags=["Websocket Chatbox"])

@websocket_auction.websocket("/{auction_id}")
async def auction_websocket_endpoint(websocket: WebSocket, auction_id : str):
    # if await websocket_auction_util_verify_user(websocket, auction_id) is False:
    #     return
    await connect(websocket, auction_id)
    try:
        while True:
            data = await websocket.receive_text()
            await broadcast(data, auction_id)
    except WebSocketDisconnect:
        disconnect(websocket, auction_id)