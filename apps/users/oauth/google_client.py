import time
import requests
from django.conf import settings
from typing import Dict, Optional, Tuple
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

class GoogleOAuthClient:
    """
    Client for handling Google OAuth operations with performance monitoring.
    """
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    def __init__(self):
        self.client_id = settings.GOOGLE_OAUTH_CLIENT_ID
        self.client_secret = settings.GOOGLE_OAUTH_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_OAUTH2_REDIRECT_URI

    def _log_performance(self, operation: str, start_time: float, end_time: float) -> None:
        """Log performance metrics for operations."""
        duration = end_time - start_time
        print(f"Performance: {operation} took {duration:.3f} seconds")

    def verify_oauth_token(self, token: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Verify an OAuth token directly (from Google Sign-In SDK)
        """
        start_time = time.time()
        try:
            # Verify the token
            id_info = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                self.client_id
            )

            # Check if token is issued by Google
            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                return None, "Wrong issuer for token"

            self._log_performance("Token Verification", start_time, time.time())
            return id_info, None

        except ValueError as e:
            return None, f"Invalid token: {str(e)}"
        finally:
            self._log_performance("Total Token Verification", start_time, time.time())

    def get_token_from_code(self, auth_code: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Exchange authorization code for access token.
        Returns tuple of (token_data, error_message)
        """
        start_time = time.time()
        
        try:
            response = requests.post(
                self.GOOGLE_TOKEN_URL,
                data={
                    'code': auth_code,
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'redirect_uri': self.redirect_uri,
                    'grant_type': 'authorization_code'
                },
                timeout=5  # Set timeout for performance monitoring
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self._log_performance("Token Exchange", start_time, time.time())
                return token_data, None
            else:
                error_msg = f"Token exchange failed: {response.text}"
                return None, error_msg

        except requests.exceptions.RequestException as e:
            return None, f"Network error during token exchange: {str(e)}"
        finally:
            self._log_performance("Total Token Exchange Operation", start_time, time.time())

    def get_user_info(self, access_token: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Fetch user information using access token.
        Returns tuple of (user_data, error_message)
        """
        start_time = time.time()
        
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(
                self.GOOGLE_USER_INFO_URL,
                headers=headers,
                timeout=5
            )

            if response.status_code == 200:
                user_data = response.json()
                self._log_performance("User Info Fetch", start_time, time.time())
                return user_data, None
            else:
                error_msg = f"User info fetch failed: {response.text}"
                return None, error_msg

        except requests.exceptions.RequestException as e:
            return None, f"Network error during user info fetch: {str(e)}"
        finally:
            self._log_performance("Total User Info Operation", start_time, time.time())

    def validate_token(self, token_data: Dict) -> bool:
        """Validate token data"""
        if not token_data:
            return False
        
        # Check if token has expired
        expires_in = token_data.get('expires_in', 0)
        token_type = token_data.get('token_type', '')
        
        return bool(expires_in > 0 and token_type.lower() == 'bearer')
