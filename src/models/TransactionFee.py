from beanie import Document, Indexed
from datetime import datetime
from fastapi import Form
from pydantic import BaseModel

class TransactionFee(Document):
    ReferenceId : str
    ReferenceType : str
    FromUserId : str
    ProductId : str
    GrossAmount : int
    FeeAmount : int 
    FeeRate : float
    Type : str
    CreatedAt : datetime



    class Settings:
        name = "TransactionFee"