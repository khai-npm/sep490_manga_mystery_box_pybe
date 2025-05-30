from beanie import Document, Indexed
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel

class Role(Document):
    role_name : str
    class Settings:
        name = "Role"
