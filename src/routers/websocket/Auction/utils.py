from bson import ObjectId
from fastapi import WebSocket
from src.models.User import User
from src.models.AuctionSession import AuctionSession
from src.libs.jwt_authenication_handler import get_current_user


async def websocket_auction_util_verify_user(websocket : WebSocket, auction_id : str):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401)
        return
    
    try:
        user = await get_current_user(token)
        curent_token_user = await User.find_one(User.username==user)


        if not curent_token_user:
            raise Exception
        
        if not await AuctionSession.find_one(AuctionSession.id == ObjectId(auction_id)):
            raise Exception

    except Exception as e:
        await websocket.close(code=1008)
        return False

    return True