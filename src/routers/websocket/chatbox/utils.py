from fastapi import WebSocket
from src.models.Conversations import Conversations
from src.models.User import User
from src.libs.jwt_authenication_handler import get_current_user
from bson import ObjectId

async def websocket_util_verify_user(websocket : WebSocket, user_id : str, conservation_id : str):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401)
        return
    
    try:
        user = await get_current_user(token)
        curent_token_user = await User.find_one(User.username==user)

        if curent_token_user.id != ObjectId(user_id):
            raise Exception
        
        current_conservation = await Conversations.find_one( 
            Conversations.id == ObjectId(conservation_id)
        )

        if not current_conservation:
            raise Exception
        
        if (current_conservation.participant_1 != str(curent_token_user.id) and
            current_conservation.participant_2 != str(curent_token_user.id)):
            raise Exception


    except Exception as e:
        await websocket.close(code=1008)
        return False

    return True