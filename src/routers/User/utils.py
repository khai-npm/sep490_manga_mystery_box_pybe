from fastapi import HTTPException
import random
import smtplib
from email.message import EmailMessage
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas.RegisterFormSchema import RegisterFormSchema
from src.models.User import User
from src.models.PendingEmailVerification import PendingEmailVerification
from src.schemas.BodyResponseSchema import BodyResponseSchema
from src.libs.regular_expression import contains_special_character
from src.libs.hash_password import hash_password_util
from datetime import datetime, timedelta
from src.libs.jwt_authenication_bearer import (authenticate_user, 
                                               create_access_token)
from src.libs.jwt_authenication_bearer import verify_password
import os
from dotenv import load_dotenv
load_dotenv()


# Email configuration
# sender_email = "your_email@gmail.com"
# receiver_email = "recipient@example.com"
# subject = "Test Email from Python"
# body = "Hello, this is a test email sent from Python."

async def delete_expire_code():
    all_data = await PendingEmailVerification.find().to_list()
    for data in all_data:
        if data.expire_time < datetime.now():
            await data.delete()


async def generate_random_string_token():
    return ''.join(str(random.randint(0, 9)) for _ in range(6))

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
            is_email_verification = False,
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

async def action_send_verfify_email(data: str):
    try:
        code = await generate_random_string_token()
        current_user = await User.find_one(User.email == data)
        
        if current_user.is_email_verification is True:
            raise Exception("already verified")
        
        new_verify_session = PendingEmailVerification(
        email=data,
        code=hash_password_util.HashPassword(code),
        expire_time=datetime.now() + timedelta(minutes=30)
        )

        await new_verify_session.insert()

        subject = "Manga Mystery Box email verify notification"
        body = "your code is: " + code
        sender_email = os.getenv("SENDER_EMAIL")

        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = data
        msg["Subject"] = subject
        msg.set_content(body)

#========================[AI generated code]====================

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, os.getenv("SENDER_PASSWORD"))
            smtp.send_message(msg)

#================================================================

        return data + "verification code sent !"

    except Exception as e:
        raise HTTPException(detail= str(e), status_code=400)

async def action_confirm_verify_email(code : str, current_user : str):
    try:
        user = await User.find_one(User.email == current_user)
        current_verify_session = await PendingEmailVerification.find_one(PendingEmailVerification.email == user.email)
        if current_verify_session.expire_time < datetime.now():
            raise Exception("invalid time")

        if verify_password(plain_pwd=code, hashed_pwd=current_verify_session.code) is False:
            raise Exception("invalid code")
        
        if user.is_email_verification is True:
            raise Exception("how can this function called ?")
        await user.set({User.is_email_verification: True})
        await current_verify_session.delete()

        return "success!"
    
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)
    


    



    

    
