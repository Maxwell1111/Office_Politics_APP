"""
Google OAuth Service - Handle OAuth 2.0 flow for Gmail and Calendar access
"""

import os
import uuid
from typing import Optional, Dict
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

# Optional imports
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests not available for OAuth")


class GoogleOAuthService:
    """
    Handle Google OAuth 2.0 flow for Gmail and Calendar API access

    Scopes requested:
    - gmail.metadata: Read email headers only (From/To/CC/timestamps)
    - calendar.events.readonly: Read calendar events
    """

    def __init__(self):
        """Initialize OAuth service with credentials from environment"""
        self.client_id = os.environ.get("GOOGLE_CLIENT_ID")
        self.client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/oauth/google/callback")

        # OAuth endpoints
        self.auth_uri = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_uri = "https://oauth2.googleapis.com/token"

        # Scopes we need
        self.scopes = [
            "https://www.googleapis.com/auth/gmail.metadata",  # Email metadata only
            "https://www.googleapis.com/auth/calendar.events.readonly",  # Calendar read
            "https://www.googleapis.com/auth/userinfo.email",  # User's email address
        ]

        # In-memory token storage (replace with database in production)
        self.token_store: Dict[str, Dict] = {}

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generate Google OAuth authorization URL

        Args:
            state: Optional state parameter for CSRF protection

        Returns:
            Authorization URL to redirect user to
        """

        if not self.client_id:
            raise ValueError("GOOGLE_CLIENT_ID not configured in environment")

        # Generate state if not provided
        if not state:
            state = str(uuid.uuid4())

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
            "access_type": "offline",  # Get refresh token
            "prompt": "consent"  # Force consent screen to get refresh token
        }

        return f"{self.auth_uri}?{urlencode(params)}"

    def exchange_code_for_tokens(self, authorization_code: str) -> Dict:
        """
        Exchange authorization code for access token and refresh token

        Args:
            authorization_code: The code returned from Google OAuth

        Returns:
            Dict with access_token, refresh_token, expires_in, etc.
        """

        if not REQUESTS_AVAILABLE:
            raise RuntimeError("requests library not available")

        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth credentials not configured")

        data = {
            "code": authorization_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }

        response = requests.post(self.token_uri, data=data, timeout=30)
        response.raise_for_status()

        tokens = response.json()

        # Calculate expiration time
        expires_in = tokens.get("expires_in", 3600)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        tokens["expires_at"] = expires_at.isoformat()

        return tokens

    def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Refresh an expired access token using refresh token

        Args:
            refresh_token: The refresh token

        Returns:
            Dict with new access_token and expires_in
        """

        if not REQUESTS_AVAILABLE:
            raise RuntimeError("requests library not available")

        data = {
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }

        response = requests.post(self.token_uri, data=data, timeout=30)
        response.raise_for_status()

        tokens = response.json()

        # Calculate expiration
        expires_in = tokens.get("expires_in", 3600)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        tokens["expires_at"] = expires_at.isoformat()

        return tokens

    def get_user_email(self, access_token: str) -> str:
        """
        Get user's email address from Google

        Args:
            access_token: Valid access token

        Returns:
            User's email address
        """

        if not REQUESTS_AVAILABLE:
            raise RuntimeError("requests library not available")

        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        return data.get("email", "")

    def store_tokens(self, user_id: str, tokens: Dict) -> None:
        """
        Store tokens for a user (in-memory for now)

        In production, store in database with encryption

        Args:
            user_id: Unique user identifier
            tokens: Token dict from OAuth
        """
        self.token_store[user_id] = {
            "access_token": tokens["access_token"],
            "refresh_token": tokens.get("refresh_token"),
            "expires_at": tokens.get("expires_at"),
            "token_type": tokens.get("token_type", "Bearer"),
            "scope": tokens.get("scope", " ".join(self.scopes))
        }

    def get_valid_access_token(self, user_id: str) -> Optional[str]:
        """
        Get a valid access token for user, refreshing if needed

        Args:
            user_id: User identifier

        Returns:
            Valid access token or None if not found
        """

        if user_id not in self.token_store:
            return None

        tokens = self.token_store[user_id]

        # Check if token is expired
        expires_at_str = tokens.get("expires_at")
        if expires_at_str:
            expires_at = datetime.fromisoformat(expires_at_str)
            now = datetime.now(timezone.utc)

            # If token expires in less than 5 minutes, refresh it
            if expires_at - now < timedelta(minutes=5):
                refresh_token = tokens.get("refresh_token")
                if refresh_token:
                    try:
                        new_tokens = self.refresh_access_token(refresh_token)
                        # Update stored tokens
                        tokens["access_token"] = new_tokens["access_token"]
                        tokens["expires_at"] = new_tokens.get("expires_at")
                        self.token_store[user_id] = tokens
                    except Exception as e:
                        print(f"Error refreshing token: {e}")
                        return None

        return tokens.get("access_token")

    def revoke_tokens(self, user_id: str) -> bool:
        """
        Revoke user's tokens and remove from storage

        Args:
            user_id: User identifier

        Returns:
            True if revoked successfully
        """

        if user_id not in self.token_store:
            return False

        tokens = self.token_store[user_id]
        access_token = tokens.get("access_token")

        if access_token and REQUESTS_AVAILABLE:
            # Revoke token with Google
            try:
                requests.post(
                    f"https://oauth2.googleapis.com/revoke?token={access_token}",
                    timeout=10
                )
            except Exception as e:
                print(f"Error revoking token with Google: {e}")

        # Remove from local storage
        del self.token_store[user_id]
        return True


# Global instance
google_oauth_service = GoogleOAuthService()
