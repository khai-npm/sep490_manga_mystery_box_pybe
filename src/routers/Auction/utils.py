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
from src.schemas.HostAuctionSchema import HostAuctionSchema
from src.schemas.AuctionWinSchema import AuctionWinSchema
from bson import ObjectId
from src.models.DigitalWallet import DigitalWallet
from bson import Decimal128
from decimal import Decimal
from src.libs.permission_checker import Permission_checker
from src.schemas.AuctionResponseSchema import AuctionResponseSchema
from dotenv import load_dotenv
import os
import asyncio
import requests

load_dotenv()
env_fee_perentage = os.getenv("FEE_PERCENT")
env_auction_duration = os.getenv("AUCTION_DURATION_MINUTES")

async def action_get_all_auction_list_user_side(filter, current_user : str):
    try:
        if filter != "default" and filter != "started" and filter != "waiting":
            raise HTTPException(status_code=400, detail="filter param not valid ! [default / started / waiting]")
        
        if filter == "waiting":
            return await action_get_waiting_auction_list_user_side(current_user)
        
        if filter == "started":
            return await action_get_started_auction_list_user_side(current_user)


        user_db = await User.find_one(User.username==current_user)
        if not user_db:
            raise HTTPException(detail="user not found!", status_code=404)
        
        return await AuctionSession.find(AuctionSession.seller_id != str(user_db.id),
                                         AuctionSession.status==1).to_list()
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)
    
async def action_get_waiting_auction_list_user_side(current_user : str):
    try:
        user_db = await User.find_one(User.username==current_user)
        if not user_db:
            raise HTTPException(detail="user not found!", status_code=404)
        
        return await AuctionSession.find(AuctionSession.seller_id != str(user_db.id),
                                         AuctionSession.status == 1,
                                         AuctionSession.start_time > datetime.now()).to_list()
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)
    
async def action_get_started_auction_list_user_side(current_user : str):
    try:
        user_db = await User.find_one(User.username==current_user)
        if not user_db:
            raise HTTPException(detail="user not found!", status_code=404)
        
        return await AuctionSession.find(AuctionSession.seller_id != str(user_db.id),
                                         AuctionSession.status == 1,
                                         AuctionSession.start_time <= datetime.now(),
                                         AuctionSession.end_time > datetime.now()).to_list()
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)
    

async def action_get_all_auction_user_hosed_side(current_user : str):
    try:
        user_db = await User.find_one(User.username==current_user)
        if not user_db:
            raise HTTPException(detail="user not found!", status_code=404)
        auction_list = await AuctionSession.find(AuctionSession.seller_id == str(user_db.id)).to_list()
        result = []
        for each in auction_list:
            fee_charge = env_fee_perentage
            incoming_value = 0
            host_value = 0
            product_auction = await AuctionProduct.find_one(AuctionProduct.auction_session_id == str(each.id))
            if product_auction:
                host_value = product_auction.current_price
                incoming_value = (product_auction.current_price - (product_auction.current_price *(int(env_fee_perentage)/100)))
            auction_response = HostAuctionSchema(
                    id = str(each.id),
                    title = each.title,
                    descripition = each.descripition,
                    start_time = each.start_time,
                    end_time = each.end_time,
                    seller_id = each.seller_id,
                    status = each.status,
                    host_value = float(host_value),
                    fee_charge=str(fee_charge) + "%",
                    incoming_value=float(incoming_value)
                )
            result.append(auction_response)


        return result
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
        duration_minutes = int(env_auction_duration)
        user = await User.find_one(User.username == current_user)
        if not user:
            raise HTTPException(detail="user not found", status_code=404)
        
        if await AuctionSession.find(AuctionSession.seller_id == str(user.id),
                                     AuctionSession.status==0,
                                     AuctionSession.end_time > datetime.now()).count() != 0:
            raise HTTPException(detail="multiple auction create has been restricted !", status_code=400)
        
        utc_vn = datetime.now(timezone(timedelta(hours=7)))
        if request_data.start_time < utc_vn +timedelta(hours=1):
            raise HTTPException(detail="start time must be above 1 hours from now", status_code=403)

        if request_data.title == "":
            raise HTTPException(detail="title not valid", status_code=400)         

        new_auction = AuctionSession(descripition=request_data.descripition,
                                     end_time=request_data.start_time + timedelta(minutes=duration_minutes),
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
        if auction_db.start_time > datetime.now() or auction_db.end_time < datetime.now():
            raise HTTPException(status_code=403, detail="auction ended or not started yet ")

        if not auction_db:
            raise HTTPException(status_code=404, detail="auction not valid !")
        
        if await AuctionParticipant.find_one(AuctionParticipant.user_id== str(user_db.id),
                                             AuctionParticipant.auction_id== auction_id) is not None:
            
            raise HTTPException(status_code=400, detail="already joined !")
        
        if auction_db.seller_id == str(user_db.id):
            raise HTTPException(status_code=403, detail="cannot join own auction session")
        
        
        # if auction_db.start_time < datetime.now():
        
        #     raise HTTPException(status_code=403, detail="auction session already started !")
        
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
    
async def action_leave_a_auction(auction_id : str, current_user_name : str):
    try:
        user_db = await User.find_one(User.username == current_user_name)
        if not user_db :
            raise HTTPException(status_code=404, detail="user not found !")
        
        auction_db = await AuctionSession.find_one(AuctionSession.id == ObjectId(auction_id))
        if not auction_db:
            raise HTTPException(status_code=404, detail="not valid auction")
        
        if auction_db.end_time > datetime.now():
            raise HTTPException(detail="cannot leave an ended auction", status_code="403")
        
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
        
        is_joined = await AuctionParticipant.find_one(AuctionParticipant.auction_id==auction_id,
                                                      AuctionParticipant.user_id == str(user_db.id))
        if not is_joined:
            raise HTTPException(status_code=403, detail="not in auction session !")
        
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
            if not session:
                return False
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
    
async def action_get_mod_auction_list_user_side(current_user : str):
    try:
        user_db = await User.find_one(User.username == current_user)
        if not user_db:
            raise HTTPException(status_code=404, detail="user not found")
        
        if await Permission_checker(current_user, "action_view_all_auction") is False:
            raise HTTPException(status_code=403, detail="access denied !")
        
        result = []

        all_auction = await AuctionSession.find().to_list()
        for each in all_auction:
            host_user = await User.find_one(User.id == ObjectId(each.seller_id))
            product_db = await AuctionProduct.find_one(AuctionProduct.auction_session_id == str(each.id))
            if product_db:
                product_id = product_db.user_product_id
                product_quantity = product_db.quantity
            else:
                product_id = ""
                product_quantity = 0
            data = AuctionResponseSchema(auction_id=str(each.id),
                                         status=each.status,
                                         host_username=host_user.username,
                                         product_id=product_id,
                                         quantity=product_quantity,
                                         start_time=each.start_time,
                                         end_time=each.end_time
                                         )
            
            result.append(data)

        return result
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

async def action_get_auction_product(auction_id : str):
    try:

        auction_db = await AuctionSession.find_one(AuctionSession.id == ObjectId(auction_id))
        if not auction_db:
            raise HTTPException(detail="auction session not found", status_code=404)
        
        product = await AuctionProduct.find_one(AuctionProduct.auction_session_id == auction_id)
        if not product:
            raise HTTPException(status_code=404, detail="no product found in this session, maybe it didn't be added ?")
        
        return product

    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

async def action_get_bid_auction(auction_id : str):
    try:
        auction_db = await AuctionSession.find_one(AuctionSession.id == ObjectId(auction_id))
        if not auction_db:
            raise HTTPException(detail="auction session not found", status_code=404)

        return await Bids.find(Bids.auction_id==auction_id).to_list()        
        
    except HTTPException as http_e:
        raise http_e
    
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))
    
async def action_get_own_win_auction(current_user : str):
    try:
        user_db = await User.find_one(User.username == current_user)
        if not current_user:
            raise HTTPException(status_code=404, detail="not found user")
        
        all_auction = await AuctionResult.find(AuctionResult.bidder_id == str(user_db.id)).to_list()
        result = []
        for each in all_auction:
            auction_info = await AuctionSession.find_one(AuctionSession.id == ObjectId(each.auction_id))
            auction_product = await AuctionProduct.find_one(AuctionProduct.auction_session_id == each.auction_id)
            auction_result_info = await AuctionResult.find_one(AuctionResult.auction_id == each.auction_id)

            new_result = AuctionWinSchema(auction_info=auction_info,
                                          auction_product=auction_product,
                                          auction_result=auction_result_info
                                          )
            
            result.append(new_result)
        return result

    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def action_get_auction_result(current_user : str):
    try:
        user_db = await User.find_one(User.username == current_user)
        if not user_db:
            raise HTTPException(status_code=404, detail="user not found")
        
        if not await Permission_checker(current_user, "action_view_all_auction_result"):
            raise HTTPException(status_code=403, detail="access denied !")
        
        all_auction_result = await AuctionResult.find().to_list()
        return all_auction_result
    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
async def action_reject_all_expired_auction():
    try:
        
        all_expired_auction = await AuctionSession.find(AuctionSession.end_time < datetime.now(),
                                                       AuctionSession.status == 0).to_list()
        for each in all_expired_auction:
            await each.set({AuctionSession.status : -1})

    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    


async def action_cancel_auction(auction_id : str, current_user : str):
    try:
        user_db = await User.find_one(User.username == current_user)
        if not user_db:
            raise HTTPException(status_code=404, detail="user not found")
        
        auction_db = await AuctionSession.find_one(AuctionSession.id == ObjectId(auction_id))
        if not auction_db:
            raise HTTPException(status_code=404, detail="auction not found")
        
        if str(user_db.id) != auction_db.seller_id:
            raise HTTPException(status_code=403, detail="requested user is not owner of auction !.")
        
        if datetime.now() > auction_db.start_time and auction_db.status == 1:
            raise HTTPException(status_code=403, detail="cannot cancel an started auction !")
        
        #await auction_db.set({AuctionSession.status : -1})
        product_auction = await AuctionProduct.find_one(AuctionProduct.auction_session_id == str(auction_db.id))
        if product_auction:
            user_product = await User_Product.find_one(User_Product.ProductId == product_auction.user_product_id,
                                                       User_Product.CollectorId==str(user_db.id))
            if user_product:
                await user_product.set({User_Product.Quantity : user_product.Quantity + product_auction.quantity})

                await product_auction.delete()

        await auction_db.delete()
        return True

    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
async def action_automated_confirmation():
    try:
        all_ended_auction = await AuctionSession.find(AuctionSession.end_time < datetime.now(),
                                                      AuctionSession.status == 1).to_list()
        for each in all_ended_auction:
            if await AuctionResult.find_one(AuctionResult.auction_id==str(each.id)):
                continue
            highest_bids_in_session = await Bids.find(Bids.auction_id == str(each.id)).sort(-Bids.bid_amount,).first_or_none()
            if highest_bids_in_session:
                auction_product = await AuctionProduct.find_one(AuctionProduct.auction_session_id == str(each.id))
                if not auction_product:
                    await each.set({AuctionSession.status : -1})
                    continue
                
                winner = await User.find_one(User.id == ObjectId(highest_bids_in_session.bidder_id))
                hoster_id = each.seller_id
                result = AuctionResult(auction_id=str(each.id),
                                       product_id=auction_product.user_product_id,
                                       quantity=auction_product.quantity,
                                       bidder_amount=Decimal(highest_bids_in_session.bid_amount),
                                       bidder_id=str(winner.id),
                                       hoster_id=hoster_id,
                                       host_claim_amount=Decimal(highest_bids_in_session.bid_amount-((highest_bids_in_session.bid_amount*5)/100)),
                                       is_solved=False
                                       )
                await result.insert()
            else:
                await each.set({AuctionSession.status : -1})
 
        
        return await action_automated_solve_auction_result()

    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
async def action_automated_solve_auction_result():
    try:
        result = []
        all_unsolved_auction_result = await AuctionResult.find(AuctionResult.is_solved==False).to_list()
        for each in all_unsolved_auction_result:
            data = await asyncio.to_thread(action_call_solve_auction_result_api, each.auction_id)
            result.append(data)
        return result

    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
def action_call_solve_auction_result_api(auction_id : str):
    url = f"https://mmb-be-dotnet.onrender.com/cs/api/AuctionSettlement/finalize-auction/{auction_id}"
    headers = {
        "accept": "text/plain"
    }

    response = requests.post(url, headers=headers, data="")
    return response.json()