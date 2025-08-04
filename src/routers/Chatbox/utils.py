from fastapi import HTTPException
from datetime import datetime
from beanie.operators import Or
from src.models.User import User
from src.models.Conversations import Conversations
from src.models.Messages import Messages
from bson import ObjectId
from src.schemas.BodyResponseSchema import BodyResponseSchema


async def action_create_conversation(user_1 : str, user_2 : str):
    try:
        target_user_1 = await User.find_one(User.username==user_1)
        target_user_2 = await User.find_one(User.id == ObjectId(user_2))

        if not target_user_1 or not target_user_2:
            raise HTTPException(status_code=404, detail="user not found!")
        
        is_current_session = await Conversations.find_one(
            Conversations.participant_1== str(target_user_1.id),
            Conversations.participant_2== str(target_user_2.id)
        )

        if is_current_session:
            return str(is_current_session.id)

        is_current_session_2 = await Conversations.find_one(
            Conversations.participant_1== str(target_user_2.id),
            Conversations.participant_2== str(target_user_1.id)
        )

        if is_current_session_2:
            return str(is_current_session_2.id)


        if not is_current_session and not is_current_session_2:
            new_conversation : Conversations = Conversations(
                participant_1=str(target_user_1.id),
                participant_2=str(target_user_2.id),
                created_at=datetime.now(),
                created_by=str(target_user_1.id)
            )

            await new_conversation.insert() 
            return str(new_conversation.id)

        else:
            raise HTTPException(status_code=403, detail="chatroom already created!")


    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)
    

async def action_get_all_messages_from_conversation(
        current_user : str, 
        id : str,
        skip: int = 0,
        limit: int = 30):

    try:
        get_user = await User.find_one(User.username==current_user)
        get_cons = await Conversations.find_one(Conversations.id == ObjectId(id))
        if not get_cons:
            raise HTTPException(status_code=404, detail="chat room not found!")
        
        if get_cons.participant_1 == str(get_user.id) or get_cons.participant_2 == str(get_user.id):
            messages_info = await Messages.find(Messages.conversation_id==id).sort("-created_at").skip(skip).limit(limit).to_list()

            return BodyResponseSchema(data= [reversed(messages_info)],
                                      length=await Messages.find(Messages.conversation_id==id).count())
        
        raise HTTPException(status_code=403, detail="You are not a participant in this conversation.")


    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)
    
async def action_get_conservation_list(username : str):
    try:
        current_user = await User.find_one(User.username == username)
        if not current_user:
            raise HTTPException(detail="User not found", status_code=404)
        
        return await Conversations.find(Or(
            Conversations.participant_1 == str(current_user.id),
            Conversations.participant_2 == str(current_user.id)
        )).to_list()
    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)

async def action_get_username_by_id(id : str):
    try:
        current_user = await User.find_one(User.id == ObjectId(id))
        if not current_user:
            raise HTTPException(detail="user not found", status_code=404)
        
        return current_user.username

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)

    
async def action_get_list_chat(current_user : str):
    
    try:
        my_user = await User.find_one(User.username == current_user)
        if not my_user:
            raise HTTPException(status_code=404, detail="user not found")
        
        my_user_id = str(my_user.id)

        userid_list = []
        conservation_list_1 = await Conversations.find(Conversations.participant_1 == my_user_id).to_list()
        for a in conservation_list_1:
            if a.participant_2 not in userid_list:
                userid_list.append(a.participant_2)

        conservation_list_2 = await Conversations.find(Conversations.participant_2 == my_user_id).to_list()
        for b in conservation_list_2:
            if b.participant_1 not in userid_list:
                userid_list.append(b.participant_1)


        return userid_list
    except HTTPException as http_e :
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    