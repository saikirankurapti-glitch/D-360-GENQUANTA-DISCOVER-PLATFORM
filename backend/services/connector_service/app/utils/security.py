import json
import base64
import hashlib
from cryptography.fernet import Fernet
from app.core.config import settings

class CredentialEncryptor:
    """
    Handles symmetrical AES-256 encryption and decryption of data source connection credentials.
    Uses the SHA-256 derived version of ENCRYPTION_KEY to initialize standard Fernet tokens.
    """
    
    def __init__(self):
        # Derive a 32-byte base64 key suitable for Fernet from the configured ENCRYPTION_KEY
        key_hash = hashlib.sha256(settings.ENCRYPTION_KEY.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(key_hash)
        self.fernet = Fernet(fernet_key)

    def encrypt(self, credentials: dict) -> str:
        """Encrypts dictionary credentials into a secure string."""
        serialized = json.dumps(credentials)
        return self.fernet.encrypt(serialized.encode()).decode()

    def decrypt(self, encrypted_str: str) -> dict:
        """Decrypts a secure string back to plaintext dictionary credentials."""
        decrypted = self.fernet.decrypt(encrypted_str.encode())
        return json.loads(decrypted.decode())

encryptor = CredentialEncryptor()
