from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas.BodyResponseSchema import BodyResponseSchema
from src.schemas.RegisterFormSchema import RegisterFormSchema
from src.routers.User.utils import (action_user_register, 
                                    action_login,
                                    action_send_verfify_email,
                                    action_confirm_verify_email)
from src.libs.jwt_authenication_handler import get_current_user, jwt_validator
from src.libs.jwt_authenication_bearer import do_refresh_token
# from src.routers.account.utils import (action_get_payment_info_by_user, action_user_register,
#                                        action_login)
# from src.lib.jwt_authenication_handler import get_current_user, jwt_validator
from src.models.User import User

User_router = APIRouter(prefix="/api/User", tags=["User"])
User_router.post("/register")



@User_router.post("/auth/register",  response_model=BodyResponseSchema)
async def register_account(new_account : RegisterFormSchema):
    return {"data" :[await action_user_register(new_account)]}

@User_router.post("/auth/login")
async def user_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return await action_login(form_data)

@User_router.post("/auth/refresh")
async def refresh_token(token : str):
    return await do_refresh_token(token)

@User_router.get("/jwt_test", dependencies=[Depends(jwt_validator)], response_model=BodyResponseSchema)
async def test_jwt():
    try:
        return {"success" : True}
    except Exception as e:
        return {"success" : False, 
                "error" : str(e)}
    
@User_router.post("/email/verify", response_model=BodyResponseSchema)
async def send_verify_email(email : str):
    return {"data" : [await action_send_verfify_email(email)]}

@User_router.post("/email/confirm", response_model=BodyResponseSchema)
async def confirm_verify_email(code : str, current_email : str):
    return {"data" : [await action_confirm_verify_email(code, current_email)]}


# @account_router.post("/login")
# async def user_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
#     return await action_login(form_data)

# @account_router.get("/jwt_test", dependencies=[Depends(jwt_validator)])
# async def test_jwt():
#     try:
#         return {"success" : True}
#     except Exception as e:
#         return {"success" : False, 
#                 "error" : str(e)}
    
# @account_router.get("/payment", response_model=BodyResponseSchema, dependencies=[Depends(jwt_validator)])
# async def get_payment_info(current_user : str = Depends(get_current_user)):
#     # return [await action_get_payment_info_by_user(current_user)]
#     return {"data" : [await action_get_payment_info_by_user(current_user)]}