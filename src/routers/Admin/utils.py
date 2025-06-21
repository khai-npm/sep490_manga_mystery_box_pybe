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

        new_role = Role(role_name=role_name)
        await new_role.insert()

    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
async def action_get_all_permission():
    try:
        all_per = Permission.find()
        return all_per.to_list()

    except HTTPException as http_e:
        raise http_e
    
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)