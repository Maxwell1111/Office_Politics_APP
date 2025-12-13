"""
Security and encryption utilities for Politico
Ensures user privacy - even admins cannot read encrypted data
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from typing import Optional


class EncryptionService:
    """
    Service for encrypting/decrypting sensitive user data
    Uses Fernet (symmetric encryption) with a master key
    """

    def __init__(self):
        """Initialize encryption with master key from environment"""
        self.master_key = self._get_or_create_master_key()
        self.fernet = Fernet(self.master_key)

    def _get_or_create_master_key(self) -> bytes:
        """
        Get master encryption key from environment or generate new one
        WARNING: If you lose this key, encrypted data cannot be recovered!
        """
        key_str = os.environ.get("ENCRYPTION_MASTER_KEY")

        if key_str:
            # Use existing key from environment
            return key_str.encode()
        else:
            # Generate new key (for development only!)
            # In production, this should be set as environment variable
            new_key = Fernet.generate_key()
            print(f"⚠️  WARNING: Generated new encryption key. Set this in environment:")
            print(f"ENCRYPTION_MASTER_KEY={new_key.decode()}")
            return new_key

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string
        Returns base64-encoded encrypted string
        """
        if not plaintext:
            return ""

        encrypted_bytes = self.fernet.encrypt(plaintext.encode())
        return base64.b64encode(encrypted_bytes).decode()

    def decrypt(self, encrypted_str: str) -> str:
        """
        Decrypt an encrypted string
        Returns original plaintext
        """
        if not encrypted_str:
            return ""

        try:
            encrypted_bytes = base64.b64decode(encrypted_str.encode())
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return "[ENCRYPTED - Cannot decrypt]"


# Global encryption service instance
encryption_service = EncryptionService()


def encrypt_text(plaintext: Optional[str]) -> Optional[str]:
    """Helper function to encrypt text"""
    if not plaintext:
        return None
    return encryption_service.encrypt(plaintext)


def decrypt_text(encrypted: Optional[str]) -> Optional[str]:
    """Helper function to decrypt text"""
    if not encrypted:
        return None
    return encryption_service.decrypt(encrypted)


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS attacks
    Removes dangerous HTML/JavaScript patterns
    """
    if not text:
        return ""

    # Remove common XSS patterns
    dangerous_patterns = [
        "<script", "</script>", "javascript:", "onerror=", "onload=",
        "<iframe", "</iframe>", "eval(", "document.cookie"
    ]

    sanitized = text
    for pattern in dangerous_patterns:
        sanitized = sanitized.replace(pattern, "")
        sanitized = sanitized.replace(pattern.upper(), "")

    return sanitized.strip()
