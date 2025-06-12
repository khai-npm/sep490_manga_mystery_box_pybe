from beanie import Document, Indexed
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel

class PendingRecoveryVerification(Document):
    email : str
    code : str
    expire_time : datetime
    wrong_code_count : int

    class Settings:
        name = "PendingRecoveryVerification"
        wrong_code_count : int