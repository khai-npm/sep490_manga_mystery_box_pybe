from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import APIKeyHeader, APIKeyQuery, OAuth2PasswordRequestForm
from src.schemas.BodyResponseSchema import BodyResponseSchema
from src.schemas.RegisterFormSchema import RegisterFormSchema
from src.schemas.PasswordRecoverySchema import PasswordRecoverySchema
from src.libs.jwt_authenication_handler import get_current_user, jwt_validator
from src.libs.jwt_authenication_bearer import do_refresh_token
from src.routers.Chatbox.utils import (action_create_conversation,
                                       action_get_all_messages_from_conversation)

# from src.routers.account.utils import (action_get_payment_info_by_user, action_user_register,
#                                        action_login)
# from src.lib.jwt_authenication_handler import get_current_user, jwt_validator
from src.models.User import User
from dotenv import load_dotenv
import os
chatbox_router = APIRouter(prefix="/api/chatbox", tags=["Chatbox"])


@chatbox_router.post("/conversation", dependencies=[Depends(jwt_validator)], response_model=BodyResponseSchema)
async def create_conversation(user_id : str, current_user : str = Depends(get_current_user)):
    return {"data" : [await action_create_conversation(current_user, user_id)]}

@chatbox_router.get("/messages", dependencies=[Depends(jwt_validator)], response_model=BodyResponseSchema)
async def get_all_messages_from_conversation(
    id : str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100), 
    current_user : str = Depends(get_current_user)):
    return await action_get_all_messages_from_conversation(current_user, id, skip, limit)

