from beanie import Document, Indexed
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel

class User(Document):
    username : str
    password : str
    email : str
    profile_image : str
    is_active : bool
    phone_number : str
    create_date : datetime
    wallet_id : str
    wrong_password_count : int
    login_lock_time : datetime
    role_id : str
    class Settings:
        name = "User"

