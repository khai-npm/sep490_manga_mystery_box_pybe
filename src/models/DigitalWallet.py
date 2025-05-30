from beanie import Document, Indexed
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel

class DigitalWallet(Document):
    ammount : int
    is_active : bool

    class Settings:
        name = "UseDigitalWallet"