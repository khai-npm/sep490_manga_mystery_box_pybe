from beanie import Document, Indexed
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel

class PendingEmailVerification(Document):
    email : str
    code : str
    expire_time : datetime

    class Settings:
        name = "PendingEmailVerification"