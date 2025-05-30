import time
import os
from dotenv import load_dotenv

import jwt
from passlib.context import CryptContext

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")



if not JWT_ALGORITHM or not JWT_SECRET:
    raise ValueError("JWT authorizer not found ! check .ENV for more info !")
print("using algo :" + JWT_ALGORITHM)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_pwd, hashed_pwd) -> bool:
    return pwd_context.verify(plain_pwd, hashed_pwd)


def get_password_hash(pwd):
    return pwd_context.hash(pwd)


def authenticate_user(user_in_db: dict, password: str) -> bool:
    if not user_in_db:
        return False
    if not verify_password(password, user_in_db["password"]):
        return False
    return True


def create_access_token(data: dict, expires_delta: float | None = None):
    to_encode = {"username": data["username"], "role":data["role_id"], "is_refresh_token" : False}
    to_encode_2 = {"username": data["username"], "role":data["role_id"], "is_refresh_token" : True}
    if expires_delta:
        expire = time.time() + expires_delta
    else:
        expire = time.time() + 3600
    to_encode.update({"exp": expire})
    encoded_token = jwt.encode(to_encode, JWT_SECRET, JWT_ALGORITHM)
    expire = expire + 3600
    to_encode_2.update({"exp": time.time()})
    encoded_token_2 = jwt.encode(to_encode_2, JWT_SECRET, JWT_ALGORITHM)
    return {
        "access_token": encoded_token,
        "refresh_token" : encoded_token_2,
        "token_type": "bearer",
        "username": data["username"],
        "role":data["role_id"],
    }

def do_refresh_token(token : str | None = None):
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

    if payload['is_refresh_token'] is True:

        payload['exp'] = time.time() + 3600
        payload['is_refresh_token'] = False

        encoded_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
        encoded_token_2 = token

        return {
        "access_token": encoded_token,
        "refresh_token" : encoded_token_2,
        "token_type": "bearer",
        "username": payload["username"],
        "role": payload["role"],
    }
    else:
        raise ValueError("refresh_token invalid !")