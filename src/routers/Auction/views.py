from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import APIKeyHeader, APIKeyQuery, OAuth2PasswordRequestForm
from src.routers.Admin.utils import action_get_all_role
from src.schemas.BodyResponseSchema import BodyResponseSchema
from src.schemas.AddAuctionProductSchema import AddAuctionProductSchema
from src.schemas.AddAuctionSessionSchema import AddAuctionSessionSchema
from src.libs.jwt_authenication_handler import get_current_user, jwt_validator
from src.libs.jwt_authenication_bearer import do_refresh_token
from src.routers.Auction.utils import (action_get_all_auction_list_user_side,
                                       action_get_all_auction_user_hosed_side,
                                       action_create_auction_product,
                                       action_create_new_auction_session,
                                       action_get_user_product_db,
                                       action_join_a_auction,
                                       leave_a_auction,
                                       action_add_bid_auction,
                                       action_total_result_ended_auction)
from src.routers.websocket.Auction.connection_manager import broadcast
from src.models.User import User
from dotenv import load_dotenv
import os

load_dotenv()

Auction = APIRouter(prefix="/api/auction", tags=["Auction"])
    
@Auction.get("/all",dependencies=[Depends(jwt_validator)], response_model=BodyResponseSchema)
async def get_all_auction_list_user_side(current_user :str = Depends(get_current_user)):
    return {"data" : [await action_get_all_auction_list_user_side(current_user)]}

@Auction.get("/me",dependencies=[Depends(jwt_validator)], response_model=BodyResponseSchema)
async def get_all_auction_user_hosed_side(current_user :str = Depends(get_current_user)):
    return {"data" : [await action_get_all_auction_user_hosed_side(current_user)]}

@Auction.get("/user-product", dependencies=[Depends(jwt_validator)], response_model=BodyResponseSchema)
async def get_user_product_db(current_user :str = Depends(get_current_user)):
    return {"data" : [await action_get_user_product_db(current_user)]}

@Auction.post("/product", dependencies=[Depends(jwt_validator)], response_model=BodyResponseSchema)
async def create_auction_product(data : AddAuctionProductSchema, current_user :str = Depends(get_current_user)):
    return {"data" : [await action_create_auction_product(data, current_user)]}

@Auction.post("/new", dependencies=[Depends(jwt_validator)], response_model=BodyResponseSchema)
async def create_new_auction_session(request_data : AddAuctionSessionSchema ,current_user : str = Depends(get_current_user)): 
    return {"data" : [await action_create_new_auction_session(request_data, current_user)]}

@Auction.post("/join", dependencies=[Depends(jwt_validator)], response_model=BodyResponseSchema)
async def join_a_auction(auction_id : str, current_user :str = Depends(get_current_user)):
    return {"data" : [await action_join_a_auction(auction_id, current_user)]}

@Auction.delete("/leave", dependencies=[Depends(jwt_validator)], response_model=BodyResponseSchema)
async def leave_a_auction(auction_id : str, current_user :str = Depends(get_current_user)):
    return {"data" : [await leave_a_auction(auction_id, current_user)]}

@Auction.post("/bid", dependencies=[Depends(jwt_validator)], response_model=BodyResponseSchema)
async def add_bid_auction(auction_id : str, ammount : float , current_user :str = Depends(get_current_user)):
    result = await action_add_bid_auction(auction_id, ammount, current_user)
    result_json = {
        "auction_id" : str(result.auction_id),
        "bid_amount" : str(result.bid_amount),
        "bid_time" : str(result.bid_time),
        "bidder_id" : str(result.bidder_id)
    }
    await broadcast(result_json, auction_id)
    return {"data" : [result]}

@Auction.post("/confirmation", dependencies=[Depends(jwt_validator)], response_model=BodyResponseSchema)
async def total_result_ended_auction(auction_id : str, current_user : str = Depends(get_current_user)):
    return {"data" : [await action_total_result_ended_auction(auction_id, current_user)]}