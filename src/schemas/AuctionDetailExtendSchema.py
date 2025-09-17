from datetime import datetime
from typing import Any, List
from pydantic import BaseModel


class AuctionDetailExtendSchema(BaseModel):
    host_username : str
    auction_id : str
    start_time : datetime
    end_time : datetime
    product_id : str
    quantity : int
    auction_current_amount : float
    transaction_fee_percent : float
    host_obtain_amount : float
    status : int

