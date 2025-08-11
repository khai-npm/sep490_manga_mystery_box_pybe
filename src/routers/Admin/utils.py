from src.models.Role import Role
from fastapi import HTTPException
from src.models.Permission import Permission
from src.models.Conversations import Conversations
from src.models.Messages import Messages
from src.models.PermissionRole import PermissionRole
from src.models.User import User
from src.libs.permission_checker import Permission_checker
from src.schemas.ModUserSchema import ModUserSchema
from src.models.TransactionHistory import TransactionHistory
from src.models.TransactionFee import TransactionFee
from src.models.AuctionSession import AuctionSession
from src.models.AuctionProduct import AuctionProduct
from datetime import datetime, timedelta
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()
MASTER_EMAIL = os.getenv("MASTER_EMAIL")
MASTER_API_KEY = os.getenv("MASTER_API_KEY")

async def action_get_all_role():
    try:
        
        return await Role.find_all().to_list()


    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)
    

async def action_change_permission_code_description(permission_code : str, desc : str):
    try:
        current_permission = await Permission.find_one(Permission.perrmission_code == permission_code)
        await current_permission.set({current_permission.permission_descripition: desc})


    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)
    

async def action_get_role_infomation_by_name(role_name : str):
    try:
        get_role = await Role.find_one(Role.role_name == role_name)
        if not get_role:
            raise HTTPException(detail="role not found", status_code=404)
        
        return get_role

    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)
    
async def action_add_new_role(role_name : str):
    try:
        if await Role.find_one(Role.role_name==role_name):
            raise HTTPException(status_code=403, detail="role_name existed !")

        new_role = Role(role_name=role_name)
        await new_role.insert()

    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
async def action_get_all_permission():
    try:
        all_per = await Permission.find_all().to_list()
        return all_per

    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)
    
async def action_delete_all_message_from_conservation(id : str):
    try:
        all_chat = Messages.find(Messages.conversation_id == id)
        async for chat in all_chat:
            print(chat)
            if not chat:
                raise HTTPException(detail="not found", status_code=404)
            await chat.delete()

        return  "all done !"
    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)

async def action_add_permission_role(role_name : str, permission_code : str):
    try:
        if await PermissionRole.find_one(PermissionRole.role_name==role_name,
                                         PermissionRole.permission_code==permission_code):
            raise HTTPException(status_code=403, detail= "PermissionRole Exist !")

        if (not await Role.find_one(Role.role_name == role_name) or
            not await Permission.find_one(Permission.perrmission_code == permission_code)
        ):
            raise HTTPException(status_code=404, detail = "invalid role or persmission code")
        
        return await PermissionRole(role_name=role_name,
                                    permission_code=permission_code).insert()

    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=400)
    

async def action_get_all_moderator_list(current_user : str):
    try:
        if await Permission_checker(current_user, "admin_view_moderator_list") is False:
            raise HTTPException(status_code=403, detail="access denied")
        
        return await User.find(User.role_id == "mod").project(ModUserSchema).to_list()

    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

async def action_get_all_user_list(current_user : str):
    try:
        if await Permission_checker(current_user, "admin_view_user_list") is False:
            raise HTTPException(status_code=403, detail="access denied")
        
        return await User.find(User.role_id == "user").project(ModUserSchema).to_list()

    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
async def action_promote_user_to_moderator(user_id : str, current_user : str):
    try:
        
        if await Permission_checker(current_user, "admin_promote_user_to_moderator") is False:
            raise HTTPException(status_code=402, detail="access denied")
        
        user_db = await User.find_one(User.id == ObjectId(user_id))
        if not user_db:
            raise HTTPException(status_code=404, detail="user not found")
        
        if user_db.role_id != "user":
            raise HTTPException(status_code=403,detail="cannot promote this user")
        
        return await user_db.set({User.role_id : "mod"})
        

    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

async def action_demote_user_moderator(user_id : str, current_user : str):
    try:
        
        if await Permission_checker(current_user, "admin_demote_moderator_to_user") is False:
            raise HTTPException(status_code=403, detail="access denied")
        
        user_db = await User.find_one(User.id == ObjectId(user_id))
        if not user_db:
            raise HTTPException(status_code=404, detail="user not found")
        
        if user_db.role_id != "mod":
            raise HTTPException(status_code=403,detail="cannot promote this user")
        
        return await user_db.set({User.role_id : "user"})
        
    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
async def action_toggle_activation_user(user_id : str, current_user : str):
    try:
        
        if await Permission_checker(current_user, "admin_manage_user") is False:
            raise HTTPException(status_code=403, detail="access denied")
        
        user_db = await User.find_one(User.id == ObjectId(user_id))
        if not user_db:
            raise HTTPException(status_code=404, detail="user not found")
        
        if user_db.role_id != "user":
            raise HTTPException(status_code=403,detail="cannot change status of this user")
        
        if user_db.is_active is True:
            await user_db.set({User.is_active : False})
        else:
            await user_db.set({User.is_active : True})

        return user_db.is_active
        

    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
async def action_get_total_trans_revenue(filter : str, current_user : str):
    try:
        if await Permission_checker(current_user, "admin_view_analyst") is False:
            raise HTTPException(status_code=403, detail="access denied")
        
        result : float = 0
        if (filter != "all" and 
            filter != "day" and
            filter != "month" and
            filter != "year"):
            raise HTTPException(status_code=400, detail="invalid filter code (all/day/month/year)")
        
        if filter == "all":
            all_trans = await TransactionHistory.find().to_list()
            for each in all_trans:
                result = result + each.Amount

        if filter == "day":
            all_trans = await TransactionHistory.find(TransactionHistory.DataTime > (datetime.now()- timedelta(days=1))).to_list()
            for each in all_trans:
                result = result + each.Amount
    
        if filter == "month":
            all_trans = await TransactionHistory.find(TransactionHistory.DataTime > (datetime.now()- timedelta(weeks=4))).to_list()
            for each in all_trans:
                result = result + each.Amount

        if filter == "year":
            all_trans = await TransactionHistory.find(TransactionHistory.DataTime > (datetime.now()- timedelta(weeks=52))).to_list()
            for each in all_trans:
                result = result + each.Amount

        return result


    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

async def action_get_total_revenue_fee(filter : str, current_user : str):
    try:
        if await Permission_checker(current_user, "admin_view_analyst") is False:
            raise HTTPException(status_code=403, detail="access denied")
        
        result : float = 0
        if (filter != "all" and 
            filter != "day" and
            filter != "month" and
            filter != "year"):
            raise HTTPException(status_code=400, detail="invalid filter code (all/day/month/year)")
        
        if filter == "all":
            all_trans = await TransactionFee.find().to_list()
            for each in all_trans:
                result = result + each.FeeAmount

        if filter == "day":
            all_trans = await TransactionFee.find(TransactionFee.CreatedAt > (datetime.now()- timedelta(days=1))).to_list()
            for each in all_trans:
                result = result + each.FeeAmount
    
        if filter == "month":
            all_trans = await TransactionFee.find(TransactionFee.CreatedAt > (datetime.now()- timedelta(weeks=4))).to_list()
            for each in all_trans:
                result = result + each.FeeAmount

        if filter == "year":
            all_trans = await TransactionFee.find(TransactionFee.CreatedAt > (datetime.now()- timedelta(weeks=52))).to_list()
            for each in all_trans:
                result = result + each.FeeAmount

        return result


    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

async def action_approve_auction_session(auction_id: str, status : int, current_user : str):
    try:
        if await Permission_checker(current_user, "moderator_auction_management") is False:
            raise HTTPException(status_code=403, detail="access denied")
        
        auction_db = await AuctionSession.find_one(AuctionSession.id == ObjectId(auction_db))
        if not auction_db:
            raise HTTPException(detail="auction session not found !", status_code=404)
        
        product_auction = await AuctionProduct.find_one(AuctionProduct.auction_session_id == auction_id)
        if not product_auction:
            raise HTTPException(detail="no product auction session is not allowed", status_code=403)
        
        if auction_db.status != 0:
            raise HTTPException(status_code=403, detail="this auction has been approved or denied")
        
        if status != 1 and status != -1:
            raise HTTPException(status_code=400, detail="invalid status : 1 - approved, -1 : denied")
        
        return await auction_db.set({AuctionSession.status : status})


    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)
