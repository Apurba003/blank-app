"""
Template Encryption Module

Provides secure encryption for biometric templates.
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os


class TemplateEncryption:
    """
    Encrypts and decrypts biometric templates using Fernet symmetric encryption.
    """
    
    def __init__(self, master_key: bytes = None):
        """
        Initialize encryption.
        
        Args:
            master_key: Master encryption key (generates new if None)
        """
        if master_key is None:
            # Get from environment or generate
            master_key_str = os.environ.get('ENCRYPTION_KEY')
            if master_key_str:
                master_key = master_key_str.encode()
            else:
                # Generate a new key (in production, this should be stored securely)
                master_key = Fernet.generate_key()
        
        if isinstance(master_key, str):
            master_key = master_key.encode()
        
        # Derive key using PBKDF2
        if len(master_key) != 32:
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'biometric_mfa_salt',  # In production, use random salt and store it
                iterations=100000,
                backend=default_backend()
            )
            derived_key = base64.urlsafe_b64encode(kdf.derive(master_key))
        else:
            derived_key = base64.urlsafe_b64encode(master_key)
        
        self.fernet = Fernet(derived_key)
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt data.
        
        Args:
            data: String data to encrypt
            
        Returns:
            Encrypted data as base64 string
        """
        if isinstance(data, str):
            data = data.encode()
        
        encrypted = self.fernet.encrypt(data)
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Decrypted string
        """
        encrypted_bytes = base64.b64decode(encrypted_data)
        decrypted = self.fernet.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key."""
        return Fernet.generate_key().decode()
