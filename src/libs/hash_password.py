import bcrypt

class hash_password_util:

    salt: bytes
    def __init__(self):
        # Adding the salt to password
        self.salt =bcrypt.gensalt()

    def HashPassword(RawPass):
        tmpPwd = bytes(RawPass,'utf-8')
        
        
        # Hashing the password
        hashed = bcrypt.hashpw(tmpPwd, bcrypt.gensalt())

        return hashed