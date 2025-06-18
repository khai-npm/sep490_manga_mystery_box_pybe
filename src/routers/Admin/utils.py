from src.models.Role import Role
from fastapi import HTTPException
from src.models.Permission import Permission

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