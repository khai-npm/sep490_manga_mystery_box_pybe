from datetime import datetime
from pydantic import BaseModel

class HostAuctionSchema(BaseModel):
    id : str
    title : str
    descripition : str
    start_time : datetime
    end_time : datetime
    seller_id : str
    status : int
    host_value : float
    fee_charge : str
    incoming_value : float