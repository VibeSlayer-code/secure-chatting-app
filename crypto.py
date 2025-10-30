#Copyright CMD Softworks
#Crypto Engine By Mor
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import secrets

class CryptoManager:
    def __init__(self, password: str):
        self.password = password
        self.key = None
        self.salt = None
        self.rotate_key()

    def rotate_key(self):
       
        self.salt = secrets.token_bytes(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=1000000,
        )
        self.key = base64.urlsafe_b64encode(kdf.derive(self.password.encode()))

    def encrypt_message(self, message: str) -> tuple[bytes, bytes]:
        
        fernet = Fernet(self.key)
        encrypted = fernet.encrypt(message.encode())
        return encrypted, self.salt

    def decrypt_message(self, encrypted: bytes, salt: bytes) -> str:
        
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=1000000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
            fernet = Fernet(key)
            return fernet.decrypt(encrypted).decode()
        except Exception:

            return "[Error: Decryption failed]"

