from beanie import Document, Indexed
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel

class Permission(Document):
    perrmission_code : str
    permission_descripition : str

    class Settings:
        name = "Permission"