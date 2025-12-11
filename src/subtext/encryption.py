"""
Encryption utilities for sensitive data (notes, messages, descriptions)
"""

import os
import base64
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend


class EncryptionService:
    """
    Service for encrypting/decrypting sensitive user data.
    Uses Fernet (symmetric encryption) with user-specific keys.
    """

    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key for a user"""
        return Fernet.generate_key().decode('utf-8')

    @staticmethod
    def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
        """
        Derive an encryption key from a user password.
        This allows client-side encryption if needed.

        Args:
            password: User password
            salt: Optional salt (generates new one if not provided)

        Returns:
            Tuple of (base64-encoded key, salt)
        """
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key.decode('utf-8'), salt

    @staticmethod
    def encrypt(data: str, encryption_key: str) -> str:
        """
        Encrypt a string using the provided key.

        Args:
            data: Plain text to encrypt
            encryption_key: Base64-encoded Fernet key

        Returns:
            Base64-encoded encrypted data
        """
        if not data:
            return ""

        try:
            f = Fernet(encryption_key.encode())
            encrypted_bytes = f.encrypt(data.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")

    @staticmethod
    def decrypt(encrypted_data: str, encryption_key: str) -> str:
        """
        Decrypt a string using the provided key.

        Args:
            encrypted_data: Base64-encoded encrypted data
            encryption_key: Base64-encoded Fernet key

        Returns:
            Decrypted plain text
        """
        if not encrypted_data:
            return ""

        try:
            f = Fernet(encryption_key.encode())
            decrypted_bytes = f.decrypt(encrypted_data.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")


# Helper functions for common use cases
def encrypt_if_key_exists(data: Optional[str], encryption_key: Optional[str]) -> Optional[str]:
    """
    Encrypt data if both data and key are provided, otherwise return data as-is.
    Useful for optional encryption scenarios.
    """
    if data and encryption_key:
        return EncryptionService.encrypt(data, encryption_key)
    return data


def decrypt_if_key_exists(encrypted_data: Optional[str], encryption_key: Optional[str]) -> Optional[str]:
    """
    Decrypt data if both data and key are provided, otherwise return data as-is.
    Useful for optional decryption scenarios.
    """
    if encrypted_data and encryption_key:
        return EncryptionService.decrypt(encrypted_data, encryption_key)
    return encrypted_data
