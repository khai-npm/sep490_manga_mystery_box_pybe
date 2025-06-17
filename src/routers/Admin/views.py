from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import APIKeyHeader, APIKeyQuery, OAuth2PasswordRequestForm
from src.routers.Admin.utils import action_get_all_role
from src.schemas.BodyResponseSchema import BodyResponseSchema
from src.schemas.RegisterFormSchema import RegisterFormSchema
from src.schemas.PasswordRecoverySchema import PasswordRecoverySchema
from src.libs.jwt_authenication_handler import get_current_user, jwt_validator
from src.libs.jwt_authenication_bearer import do_refresh_token
# from src.routers.account.utils import (action_get_payment_info_by_user, action_user_register,
#                                        action_login)
# from src.lib.jwt_authenication_handler import get_current_user, jwt_validator
from src.models.User import User
from dotenv import load_dotenv
import os

load_dotenv()
MASTER_API_KEY = os.getenv("MASTER_API_KEY")

admin_router = APIRouter(prefix="/api/admin", tags=["Administrator"])
admin_router.post("/ali")

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)


async def get_api_key(
    api_key_header: str = Depends(api_key_header),
    api_key_query: str = Depends(api_key_query)
):
    if api_key_header == MASTER_API_KEY or api_key_query == MASTER_API_KEY:
        return MASTER_API_KEY
    else:
        raise HTTPException(
            status_code=403,
            detail="Could not validate API key"
        )
    
@admin_router.get("/role/", response_model=BodyResponseSchema)
async def protected_route(api_key: str = Depends(get_api_key)):
    return {"data": [await action_get_all_role()]}