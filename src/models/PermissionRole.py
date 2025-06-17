from beanie import Document, Indexed
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel

class PermissionRole(Document):
    permission_code : str
    role_name : str

    class Settings:
        name = "PermissionRole"