from datetime import datetime, timedelta
from src.models.User import User
from src.models.AuctionSession import AuctionSession
from src.models.User_Product import User_Product
from src.models.AuctionProduct import AuctionProduct
from fastapi import HTTPException
from src.schemas.AddAuctionProductSchema import AddAuctionProductSchema
from src.schemas.AddAuctionSessionSchema import AddAuctionSessionSchema

async def action_get_all_auction_list_user_side(current_user : str):
    try:
        user_db = await User.find_one(User.username==current_user)
        if not user_db:
            raise HTTPException(detail="user not found!", status_code=404)
        
        return await AuctionSession.find(AuctionSession.seller_id != str(user_db.id)).to_list()
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)
    

async def action_get_all_auction_user_hosed_side(current_user : str):
    try:
        user_db = await User.find_one(User.username==current_user)
        if not user_db:
            raise HTTPException(detail="user not found!", status_code=404)
        
        return await AuctionSession.find(AuctionSession.seller_id == str(user_db.id)).to_list()
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)
    

async def action_create_auction_product(request_data : AddAuctionProductSchema , current_user : str):
    try:
        user = await User.find_one(User.username == current_user)
        if not user:
            raise HTTPException(detail="user not found", status_code=404)
        user_product = await User_Product.find_one(User_Product.ProductId == request_data.product_id)
        if not user_product:
            raise HTTPException(detail="product user not found", status_code=404)
        
        if user_product.Quantity - request_data.quantity < 0:
            raise HTTPException(detail="quantity not valid", status_code=400)
        
        if request_data.starting_price < 0 :
            raise HTTPException(detail="price not vlaid", status_code=400)
        
        new_auction_product = AuctionProduct(auction_session_id=None,
                                             quantity= request_data.quantity,
                                             seller_id=str(user.id),
                                             starting_price=request_data.starting_price,
                                             status=0,
                                             user_product_id=str(user_product.id))
        
        await user_product.set({User_Product.Quantity : user_product.Quantity-request_data.quantity})
        await new_auction_product.insert()
        
        
        

    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)
    

async def action_create_new_auction_session(request_data : AddAuctionSessionSchema, current_user : str):
    try:
        user = await User.find_one(User.username == current_user)
        if not user:
            raise HTTPException(detail="user not found", status_code=404)
        
        if request_data.start_time < datetime.now()+timedelta(hours=4):
            raise HTTPException(detail="start time must be above 4 hours from now", status_code=400)
        
        if request_data.end_time < request_data.start_time:
            raise HTTPException(detail="invalid end time !", status_code=400)

        if request_data.title == "":
            raise HTTPException(detail="title not valid", status_code=400)         

        new_auction = AuctionSession(descripition=request_data.descripition,
                                     end_time=request_data.end_time,
                                     start_time=request_data.start_time,
                                     seller_id=str(user.id),
                                     title=request_data.title,
                                     status=0)
        
        await new_auction.insert()

    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)
    
async def action_get_user_product_db(current_user : str):
    try:
        db_user = await User.find_one(User.username == current_user)
        if not db_user:
            raise HTTPException(detail="user not found !", status_code=404)
        
        user_product_list = await User_Product.find(User_Product.CollectorId==str(db_user.id)).to_list()

        return user_product_list

    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)
        