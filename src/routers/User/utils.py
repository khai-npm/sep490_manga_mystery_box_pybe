import re
from fastapi import HTTPException
import random
import smtplib
from email.message import EmailMessage
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas.RegisterFormSchema import RegisterFormSchema
from src.models.User import User
from src.models.PendingEmailVerification import PendingEmailVerification
from src.models.PendingRecoveryVerification import PendingRecoveryVerification
from src.schemas.BodyResponseSchema import BodyResponseSchema
from src.libs.regular_expression import contains_special_character
from src.libs.hash_password import hash_password_util
from src.schemas.PasswordRecoverySchema import PasswordRecoverySchema
from datetime import datetime, timedelta
from src.libs.jwt_authenication_bearer import (authenticate_user, 
                                               create_access_token)
from src.libs.check_exist_mail import is_valid_email
from src.libs.jwt_authenication_bearer import verify_password
import os
from dotenv import load_dotenv
load_dotenv()


# Email configuration
# sender_email = "your_email@gmail.com"
# receiver_email = "recipient@example.com"
# subject = "Test Email from Python"
# body = "Hello, this is a test email sent from Python."


def check_password(password):
    print("this is running")
    if len(password) < 8 or len(password) > 35:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

async def delete_expire_code():
    all_data = await PendingEmailVerification.find().to_list()
    for data in all_data:
        if data.expire_time < datetime.now():
            await data.delete()

    all_data2 = await PendingRecoveryVerification.find().to_list()
    for data2 in all_data2:
        if data2.expire_time < datetime.now():
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
        
        if not (3 <= len(request_data.username) <= 30):
            return HTTPException(detail="username's length must be in 3 -> 10 character")

        if not re.match(r"^[a-zA-Z0-9_]+$", request_data.username):
            raise HTTPException(detail="username only able for containing letter, number and underscore")

        if await User.find_one(User.username == request_data.username):
            raise HTTPException(detail="username already exist", status_code=400)
        
        if await User.find_one(User.email == request_data.email) is not None:
            raise Exception("registered email")
        
        if check_password(request_data.password) is False:
            raise Exception("Password must be at least 8 characters, include uppercase, lowercase, number, and special character.")

        if is_valid_email(request_data.email) is False:
            raise Exception("email not existed")
        
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
        email_db_user = await User.find_one(User.email == from_data.username)
        if email_db_user:
            if email_db_user.is_active is False:
                          raise Exception("inactive account")

            email_db_user = email_db_user.model_dump()

            if not authenticate_user(email_db_user, from_data.password):
                raise Exception("incorrect username or password!")
            
            return create_access_token(email_db_user)



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

        if await User.find_one(User.email == data) is None:
            raise Exception("email not in system")
        
        is_in_curent_session = await PendingEmailVerification.find_one(PendingEmailVerification.email==data)
        
        if is_in_curent_session is not None:
            # time = datetime.now() - (is_in_curent_session.expire_time - timedelta(minutes=30))
            if datetime.now() - (is_in_curent_session.expire_time - timedelta(minutes=30)) < timedelta(seconds=30):
                raise Exception("re-send waiting time is 30s, try again later")
            
            else:
                await is_in_curent_session.delete()


        await delete_expire_code()
        code = await generate_random_string_token()
        current_user = await User.find_one(User.email == data)
        
        if current_user.is_email_verification is True:
            raise Exception("already verified")
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_file_path = os.path.join(current_dir, "..", "email_pattern.html")
        print(os.getcwd())
        with open("./src/email_box.html", "r", encoding="utf-8") as f:
            html_template = f.read()
        html_content = html_template.replace("{code}", code)

        
        
        new_verify_session = PendingEmailVerification(
        email=data,
        code=hash_password_util.HashPassword(code),
        expire_time=datetime.now() + timedelta(minutes=5),
        wrong_code_count=0
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
        msg.add_alternative(html_content, subtype='html')

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
        
        if current_verify_session.wrong_code_count > 5:
            await current_verify_session.delete()
            raise Exception(" retry attemp's limit exeeded!  re-send OTP to start verification again")

        if verify_password(plain_pwd=code, hashed_pwd=current_verify_session.code) is False:
            await current_verify_session.set({PendingEmailVerification.wrong_code_count : current_verify_session.wrong_code_count+1})
            raise Exception("invalid code")
        
        if user.is_email_verification is True:
            raise Exception("how can this function called ?")
        
        await user.set({User.is_email_verification: True})
        await current_verify_session.delete()
        await delete_expire_code()

        return "success!"
    
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)
    
async def action_send_recovery_email(data : str):
    try:

        if await User.find_one(User.email == data) is None:
            raise Exception("email not in system")
        
        is_in_curent_session = await PendingRecoveryVerification.find_one(PendingRecoveryVerification.email==data)
        
        if is_in_curent_session is not None:
            # time = datetime.now() - (is_in_curent_session.expire_time - timedelta(minutes=30))
            if datetime.now() - (is_in_curent_session.expire_time - timedelta(minutes=30)) < timedelta(seconds=30):
                raise Exception("re-send waiting time is 30s, try again later")
            
            else:
                await is_in_curent_session.delete()


        await delete_expire_code()
        code = await generate_random_string_token()
        current_user = await User.find_one(User.email == data)
        
        # current_dir = os.path.dirname(os.path.abspath(__file__))
        # html_file_path = os.path.join(current_dir, "..", "email_pattern.html")
        with open("./src/recovery_box.html", "r", encoding="utf-8") as f:
            html_template = f.read()
        html_content = html_template.replace("{code}", code)

        
        
        new_verify_session = PendingRecoveryVerification(
        email=data,
        code=hash_password_util.HashPassword(code),
        expire_time=datetime.now() + timedelta(minutes=5),
        wrong_code_count=0
        )

        await new_verify_session.insert()

        subject = "Manga Mystery Box email verify notification"
        body = "email recovery: " + code
        sender_email = os.getenv("SENDER_EMAIL")


        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = data
        msg["Subject"] = subject
        msg.set_content(body)
        msg.add_alternative(html_content, subtype='html')


        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, os.getenv("SENDER_PASSWORD"))
            smtp.send_message(msg)


        return data + " verification code sent !"

    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)


async def action_confirm_recovery_request(data : PasswordRecoverySchema):
    try:
            
            current_verification_session : PendingRecoveryVerification = await PendingRecoveryVerification.find_one(PendingRecoveryVerification.email == data.email)
            if not current_verification_session:
                raise HTTPException(detail="verification not found" , status_code=404)
            
            if current_verification_session.wrong_code_count > 5:
                await current_verification_session.delete()
                raise Exception("retry attemp's limit exeeded!  re-send OTP to start verification again")
            
            if current_verification_session.expire_time < datetime.now():
                raise Exception("invalid time")

            if verify_password(plain_pwd=data.code, hashed_pwd=current_verification_session.code) is False:
                await current_verification_session.set({PendingRecoveryVerification.wrong_code_count: current_verification_session.wrong_code_count+1})
                raise Exception("invalid code")
            
            current_user : User = await User.find_one(User.email == data.email)
            if not current_user:
                raise HTTPException(detail="user not found", status_code=404)
            
            await current_user.set({User.password: hash_password_util.HashPassword(data.password)})
            await current_verification_session.delete()
            delete_expire_code()
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)

    
    


    



    

    
