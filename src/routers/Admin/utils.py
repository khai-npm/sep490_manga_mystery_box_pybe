from src.models.Role import Role
from fastapi import HTTPException


async def action_get_all_role():
    try:
        
        return await Role.find_all().to_list()


    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)