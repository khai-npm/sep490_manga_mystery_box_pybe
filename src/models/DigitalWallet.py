from beanie import Document, Indexed
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel, field_validator
from bson import Decimal128
from decimal import Decimal

class DigitalWallet(Document):
    ammount : Decimal
    is_active : bool

    # Validator xử lý khi lấy dữ liệu từ MongoDB (do beanieODM không hiểu Decimal128 là gì) 
    @field_validator("ammount", mode="before")
    @classmethod
    def convert_decimal128(cls, v):
        if isinstance(v, Decimal128):
            return v.to_decimal()
        return v
    
    class Settings:
        name = "UseDigitalWallet"