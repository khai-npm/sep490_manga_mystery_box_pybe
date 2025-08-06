from datetime import datetime, timedelta, timezone
from src.models.User import User
from src.models.AuctionSession import AuctionSession
from src.models.User_Product import User_Product
from src.models.AuctionProduct import AuctionProduct
from src.models.AuctionParticipant import AuctionParticipant
from src.models.Bids import Bids
from src.models.AuctionWinner import AuctionWinner
from src.models.AuctionResult import AuctionResult
from fastapi import HTTPException
from src.schemas.AddAuctionProductSchema import AddAuctionProductSchema
from src.schemas.AddAuctionSessionSchema import AddAuctionSessionSchema
from bson import ObjectId
from src.models.DigitalWallet import DigitalWallet
from bson import Decimal128
from decimal import Decimal
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
        user_product = await User_Product.find_one(User_Product.ProductId == request_data.product_id,
                                                   User_Product.CollectorId==str(user.id))
        if not user_product:
            raise HTTPException(detail="product user not found", status_code=404)
    

        
        if user_product.Quantity - request_data.quantity < 0:
            raise HTTPException(detail="quantity not valid", status_code=400)
        
        if request_data.starting_price < 0 :
            raise HTTPException(detail="price not valid", status_code=400)
        
        if not await AuctionSession.find_one(AuctionSession.id == ObjectId(request_data.auction_session_id)):
            raise HTTPException(detail="auction not found !", status_code=404)
        
        exist_product = await AuctionProduct.find_one(AuctionProduct.user_product_id == str(user_product.id))
        if exist_product:
            raise HTTPException(detail="product already exist !", status_code=400)
        
        new_auction_product = AuctionProduct(auction_session_id=request_data.auction_session_id,
                                             quantity= request_data.quantity,
                                             seller_id=str(user.id),
                                             starting_price=request_data.starting_price,
                                             current_price=request_data.starting_price,
                                             status=0,
                                             user_product_id=user_product.ProductId)
        
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
        
        if await AuctionSession.find(AuctionSession.seller_id == str(user.id),
                                     AuctionSession.status==0).count() != 0:
            raise HTTPException(detail="multiple auction create has been restricted !", status_code=400)
        
        utc_vn = datetime.now(timezone(timedelta(hours=7)))
        if request_data.start_time < utc_vn +timedelta(hours=1):
            raise HTTPException(detail="start time must be above 1 hours from now", status_code=403)

        if request_data.title == "":
            raise HTTPException(detail="title not valid", status_code=400)         

        new_auction = AuctionSession(descripition=request_data.descripition,
                                     end_time=request_data.start_time + timedelta(hours=1),
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
        

async def action_join_a_auction(auction_id : str, current_user_name : str):
    try:
        user_db = await User.find_one(User.username == current_user_name)
        if not user_db :
            raise HTTPException(status_code=404, detail="user not found !")
        
        auction_db = await AuctionSession.find_one(AuctionSession.id == ObjectId(auction_id))

        if not auction_db:
            raise HTTPException(status_code=404, detail="auction not valid !")
        
        if await AuctionParticipant.find_one(AuctionParticipant.user_id== str(user_db.id),
                                             AuctionParticipant.auction_id== auction_id) is not None:
            
            raise HTTPException(status_code=400, detail="already joined !")
        
        if auction_db.seller_id == str(user_db.id):
            raise HTTPException(status_code=403, detail="cannot join own auction session")
        
        
        if auction_db.start_time < datetime.now():
        
            raise HTTPException(status_code=403, detail="auction session already started !")
        
        product = await AuctionProduct.find_one(AuctionProduct.auction_session_id == auction_id)
        if not product:
            raise HTTPException(status_code=403, detail="no product included ! cannot join in")
        

        join_info = AuctionParticipant(auction_id=auction_id,
                                       user_id=str(user_db.id))
        
        return await join_info.insert()
        
    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail= str(e))
    
async def leave_a_auction(auction_id : str, current_user_name : str):
    try:
        user_db = await User.find_one(User.username == current_user_name)
        if not user_db :
            raise HTTPException(status_code=404, detail="user not found !")
        
        auction_participant = await AuctionParticipant.find_one(AuctionParticipant.user_id== str(user_db.id),
                                             AuctionParticipant.auction_id== auction_id)
        
        if not auction_participant:
            raise HTTPException(status_code=404, detail="user not found !")
        
        return await auction_participant.delete()



    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
async def action_add_bid_auction(auction_id : str, ammount : float, current_user : str):
    try:
        user_db = await User.find_one(User.username == current_user)
        if not user_db:
            raise HTTPException(status_code=404, detail="user not found !")
        
        auction_db = await AuctionSession.find_one(AuctionSession.id == ObjectId(auction_id))
        if not auction_db:
            raise HTTPException(status_code=404, detail="auction not found")
        
        user_wallet = await DigitalWallet.find_one(DigitalWallet.id == ObjectId(user_db.wallet_id))
        if not user_wallet:
            raise HTTPException(status_code=403, detail="wallet not registered !")
        
        if ammount > user_wallet.ammount:
            raise HTTPException(status_code=403, detail="insuffient ammount !")
        
        if auction_db.start_time > datetime.now() or datetime.now() > auction_db.end_time:
            raise HTTPException(status_code=403, detail="auction session closed or not open yet!")
        
        product_auction = await AuctionProduct.find_one(AuctionProduct.auction_session_id == auction_id)
        if not product_auction:
            raise HTTPException(status_code=403, detail="product info not found !")
        
        if product_auction.starting_price > ammount:
            raise HTTPException(status_code=403, detail="bidding ammount is less than product's starting price")
        
        # all_bids_in_session = await Bids.find(Bids.auction_id == (auction_db.id)).sort(-Bids.bid_amount).to_list()
        # highest_bids_in_session = all_bids_in_session[0]
        highest_bids_in_session = await Bids.find(Bids.auction_id == str(auction_db.id)).sort(-Bids.bid_amount,).first_or_none()
        print(highest_bids_in_session)

        if not highest_bids_in_session:
            # await user_wallet.set({DigitalWallet.ammount : DigitalWallet.ammount - ammount})
            await product_auction.set({AuctionProduct.current_price : ammount})
            return await Bids(auction_id=str(auction_db.id),
                              bid_amount=ammount,
                              bidder_id=str(user_db.id),
                              bid_time=datetime.now()).insert()

        if ammount <= highest_bids_in_session.bid_amount + ((product_auction.starting_price * 5)/100):
            raise HTTPException(status_code=403, detail="bid ammount invalid")
        
        else:
            # await user_wallet.set({DigitalWallet.ammount : DigitalWallet.ammount - ammount})
            await product_auction.set({AuctionProduct.current_price : ammount})
            return await Bids(auction_id=str(auction_db.id),
                              bid_amount=ammount,
                              bidder_id=str(user_db.id),
                              bid_time=datetime.now()).insert()
            
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

async def action_total_result_ended_auction(auction_id : str, current_user : str):
    try:
        if await AuctionResult.find_one(AuctionResult.auction_id==auction_id):
            raise HTTPException(status_code=403, detail="auction already confirmed !")

        user_db = await User.find_one(User.username == current_user)
        if not user_db:
            raise HTTPException(status_code=404, detail="user not found")
        auction_db = await AuctionSession.find_one(AuctionSession.id == ObjectId(auction_id))

        if not auction_db:
            raise HTTPException(status_code=404, detail="auction session not found")
        
        if str(user_db.id) != auction_db.seller_id:
            raise HTTPException(status_code=403, detail="requested user is not owner of auction !.")
        
        if datetime.now() < auction_db.end_time :
            raise HTTPException(status_code=403, detail="auction session not yet ended !")
        
        highest_bids_in_session = await Bids.find(Bids.auction_id == auction_id).sort(-Bids.bid_amount,).first_or_none()
        if not highest_bids_in_session:
            raise HTTPException(status_code=404, detail="not found highest BID")
        
        auction_product = await AuctionProduct.find_one(AuctionProduct.auction_session_id == str(auction_db.id))

        if not auction_product:
            raise HTTPException(status_code=403, detail="product data conflicted !")
        
        winner = await User.find_one(User.id == ObjectId(highest_bids_in_session.bidder_id))
        hoster_id = auction_db.seller_id
        result = AuctionResult(auction_id=auction_id,
                               product_id=auction_product.user_product_id,
                               quantity=auction_product.quantity,
                               bidder_amount=Decimal(highest_bids_in_session.bid_amount),
                               bidder_id=str(winner.id),
                               hoster_id=hoster_id,
                               host_claim_amount=Decimal(highest_bids_in_session.bid_amount-((highest_bids_in_session.bid_amount*5)/100)),
                               is_solved=False
                               )
        
        
        return await result.insert()

    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

async def action_is_joined_auction(current_user : str):
    try:

        user_db = await User.find_one(User.username == current_user)
        if not user_db:
            raise HTTPException(status_code=404, detail="user not found")

        joined_auction = await AuctionParticipant.find(AuctionParticipant.user_id==str(user_db.id)).to_list()
        for auction in joined_auction:
            session = await AuctionSession.find_one(AuctionSession.id == ObjectId(auction.auction_id))
            if session.start_time < datetime.now() < session.end_time:
                return True
            
        return False

    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    


async def action_get_joined_history_auction(current_user : str):
    try:
        user_db = await User.find_one(User.username == current_user)
        if not user_db:
            raise HTTPException(status_code=404, detail="user not found")
        auction_list = []
        particited_auction = await AuctionParticipant.find(AuctionParticipant.user_id==str(user_db.id)).to_list()
        for each in particited_auction:
            auction = await AuctionSession.find_one(AuctionSession.id == ObjectId(each.auction_id))
            if auction.end_time < datetime.now():
                auction_list.append(auction)

        return auction_list


    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))