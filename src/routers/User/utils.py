from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas.RegisterFormSchema import RegisterFormSchema
from src.models.User import User
from src.schemas.BodyResponseSchema import BodyResponseSchema
from src.libs.regular_expression import contains_special_character
from src.libs.hash_password import hash_password_util
from datetime import datetime
from src.libs.jwt_authenication_bearer import (authenticate_user, 
                                               create_access_token)

async def action_user_register(request_data : RegisterFormSchema):
    try:
        if (request_data.username == "" or
            request_data.password =="" or
             request_data.email == "" ):

            raise HTTPException(detail="data input invalid", status_code=401)
        
        if (" " in request_data.username or
            " " in request_data.password or
            " " in request_data.email ):
            raise HTTPException(detail="data input invalid", status_code=400)
        
        if contains_special_character(request_data.username):
            raise HTTPException(detail="data input invalid", status_code=400)

        if await User.find_one(User.username == request_data.username):
            raise HTTPException(detail="username already exist", status_code=400)
        
        new_account = User(
            username = request_data.username,
            password = hash_password_util.HashPassword(request_data.password),
            create_date=datetime.now(),
            email=request_data.email,
            profile_image = "",
            is_active = True,
            phone_number="",
            wallet_id="",
            wrong_password_count=0,
            login_lock_time=datetime.now(),
            role_id="",
        )
        
        await new_account.insert()

        return "account registered successfully!"
        


    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)
    


async def action_login(from_data : OAuth2PasswordRequestForm):
    try:
        user_in_db = await User.find_one(User.username == from_data.username)
        if not user_in_db:
            raise HTTPException(detail="account not found", status_code=404)
        
        if user_in_db.is_active is False:
            raise Exception("inactive account")
        
        user_in_db = user_in_db.model_dump()
        
        if not authenticate_user(user_in_db, from_data.password):
            raise Exception("incorrect username or password!")

        return create_access_token(user_in_db)
    
    except Exception as e:
        return BodyResponseSchema(success=False, error=str(e))