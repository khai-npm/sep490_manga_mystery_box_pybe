from src.models.User import User
from src.models.AuctionSession import AuctionSession
from fastapi import HTTPException


async def action_get_all_auction_list_user_side(current_user : str):
    try:
        user_db = await User.find_one(User.username==current_user)
        if not user_db:
            raise HTTPException(detail="user not found!", status_code=404)
        
        return await AuctionSession.find(AuctionSession.seller_id != str(user_db.id))
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)
    

async def action_get_all_auction_user_hosed_side(current_user : str):
    try:
        user_db = await User.find_one(User.username==current_user)
        if not user_db:
            raise HTTPException(detail="user not found!", status_code=404)
        
        return await AuctionSession.find(AuctionSession.seller_id == str(user_db.id))
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)