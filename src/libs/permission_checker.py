from src.models.User import User
from src.models.Permission import Permission
from src.models.PermissionRole import PermissionRole
from src.models.Role import Role
from bson import ObjectId

async def Permission_checker(username, input_permission_code):

    try:
        user_role = await Permission.find_one(Permission.perrmission_code == input_permission_code)
        if not user_role:
            new_per : Permission = Permission(perrmission_code=input_permission_code, permission_descripition="")
            await new_per.insert()

        current_user : User = await User.find_one(User.username==username)
        if not current_user:
            return False
        
    
        # current_role : Role = Role.find_one(Role.id == ObjectId(current_user.role_id))
        if await PermissionRole.find_one(PermissionRole.role_name==current_user.role_id,
                                    PermissionRole.permission_code=="*"):
            return True
        
    
        if not await PermissionRole.find_one(PermissionRole.role_name==current_user.role_id,
                                    PermissionRole.permission_code==input_permission_code):
            return False
    
        return True
    
    except Exception as e:
        print(str(e))
        return False