from beanie import Document, Indexed
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel

class PermissionRole(Document):
    permission_id : str
    role_id : str

    class Settings:
        name = "PermissionRole"