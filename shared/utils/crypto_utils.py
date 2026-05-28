import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class EncryptionService:
    """Helper for symmetric encryption using Fernet (AES-128 in CBC mode)."""
    
    @staticmethod
    def generate_key_from_password(password: str, salt: bytes = b'tether_salt_2024') -> str:
        """Derives a stable 32-byte key from a password and salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key.decode()

    def __init__(self, key: str = None):
        if not key:
            # For this MVP, we'll use a fixed key if none provided. 
            # In Phase 6 (E2EE), we will implement DH key exchange.
            key = base64.urlsafe_b64encode(b'tether_default_32_byte_secret_key!')
            
        self.fernet = Fernet(key)

    def encrypt(self, plain_text: str) -> str:
        """Encrypts a string and returns a base64 encoded token."""
        return self.fernet.encrypt(plain_text.encode()).decode()

    def decrypt(self, encrypted_token: str) -> str:
        """Decrypts a base64 encoded token and returns the plain string."""
        try:
            return self.fernet.decrypt(encrypted_token.encode()).decode()
        except Exception:
            return "[Decryption Error: Invalid Key or Corrupted Data]"
