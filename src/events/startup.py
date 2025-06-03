from datetime import datetime
from beanie import init_beanie

from src.libs.hash_password import hash_password_util



async def event_01_init_db():
    import os

    # from src.models.account import account
    # from src.models.participant import participant
    # from src.models.payment import payment
    # from src.models.server import server
    # from src.models.task import task
    # from src.models.token import token
    from src.models.User import User
    from src.models.DigitalWallet import DigitalWallet
    from src.models.Permission import Permission
    from src.models.PermissionRole import PermissionRole
    from src.models.Role import Role
    from src.models.PendingEmailVerification import PendingEmailVerification
    from motor.motor_asyncio import AsyncIOMotorClient
    from src.database.get_db_instance import connection_string

    if not connection_string:
        raise ValueError("connection string not found. check .ENV is exist or not! ")
    print("Connected Database set: " + connection_string)
    db_instance = AsyncIOMotorClient(connection_string)
    await init_beanie(
        database=db_instance["SEP_MMB_DB"], document_models=[User, 
                                                             DigitalWallet, 
                                                             Permission, 
                                                             PermissionRole, 
                                                             Role,
                                                             PendingEmailVerification]
    )
    # if await account.count() == 0:
    #     new_account = account(username="admin",
    #                             password=hash_password_util.HashPassword("1"), 
    #                             create_date=datetime.now(), 
    #                             wallet=0,
    #                             token_id= [""],
    #                             discord_user_id="",
    #                             payment_info_id=[""],
    #                             role = 2,
    #                             status=True
    #                             )
    #     await new_account.insert()
    #     print("insert new admin account")

    if await Permission.count() == 0:
        print("permission document not found! improting sample data....")
        new_permission = Permission(
            permission_name="sample permission",
            perrmission_code="PER_SAMPLE_0",
            permission_descripition="only for database testing"
        )
        await new_permission.insert()
        print("sample permission imported")



    if await Role.count() ==  0:
        print("Role document not found! improting sample data....")
        new_role = Role(
            role_name= "sample role"
        )

        await new_role.insert()

    if await PermissionRole.count() == 0:
                
        print("PermissionRole document not found! improting sample data....")
        new_per_role = PermissionRole(permission_id="sample", role_id="sample")
        await new_per_role.insert()
        print("PermissionRole permission imported")



    

    if await User.count() == 0:
        print("user document not found! improting sample data....")
        new_user = User(username = "sample_data",
                        password = hash_password_util.HashPassword("1"),
                        create_date=datetime.now(),
                        email="sample",
                        profile_image = "sample",
                        is_active = False,
                        phone_number="sample",
                        wallet_id="sample",
                        is_email_verification = False,
                        wrong_password_count=0,
                        login_lock_time=datetime.now(),
                        role_id="sample",
                        )
        await new_user.insert()
        print("sample user imported")


    if await DigitalWallet.count() == 0:
        print("Digital Wallet document not found! improting sample data....")
        new_wallet = DigitalWallet(
            ammount=0,
            is_active=False
        )

        await new_wallet.insert()
        print("sample DigitalWallet imported")


events = [v for k, v in locals().items() if k.startswith("event_")]