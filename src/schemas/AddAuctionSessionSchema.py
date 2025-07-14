from datetime import datetime
from typing import Any, List
from pydantic import BaseModel


class AddAuctionSessionSchema(BaseModel):
    title : str
    descripition : str
    start_time : datetime
    end_time : datetime