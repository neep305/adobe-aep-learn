#!/usr/bin/env python3
"""
Adobe Experience Platform Authentication Helper

Supports both OAuth Server-to-Server (recommended) and JWT (legacy) authentication.
Automatically handles token caching and refresh.
"""

import json
import jwt
import time
import requests
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

class AEPAuthHelper:
    """Adobe Experience Platform Authentication Helper

    Supports two authentication methods:
    1. OAuth Server-to-Server (recommended)
    2. JWT (legacy - being deprecated)

    The authentication method is auto-detected from config file.
    """

    TOKEN_URL_OAUTH = 'https://ims-na1.adobelogin.com/ims/token/v3'
    TOKEN_URL_JWT = 'https://ims-na1.adobelogin.com/ims/exchange/jwt'

    def __init__(self, config_path):
        """Initialize with config file containing credentials

        Args:
            config_path: Path to JSON config file

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

        # Auto-detect auth method
        self.auth_method = self._detect_auth_method()

        # Setup token cache with secure permissions
        self.token_cache_path = Path.home() / '.aep_token_cache.json'
        self.access_token = None
        self.token_expiry = None

    def _detect_auth_method(self):
        """Detect authentication method from config"""
        if 'auth_method' in self.config:
            method = self.config['auth_method'].lower()
            if method not in ['oauth', 'jwt']:
                raise ValueError(f"Invalid auth_method: {method}. Must be 'oauth' or 'jwt'")
            return method

        # Auto-detect based on fields present
        if 'private_key_path' in self.config or 'technical_account_id' in self.config:
            print("⚠️  Warning: Detected JWT authentication (legacy). Consider migrating to OAuth.", file=sys.stderr)
            return 'jwt'
        else:
            return 'oauth'
    
    def get_access_token(self):
        """Get valid access token, using cache if available

        Returns:
            str: Valid access token

        Raises:
            Exception: If token generation fails
        """
        # Check cache first
        if self._is_token_valid():
            print(f"✓ Using cached token (expires: {self.token_expiry})")
            return self.access_token

        # Generate new token based on auth method
        print(f"⟳ Generating new access token using {self.auth_method.upper()}...")

        try:
            if self.auth_method == 'oauth':
                self.access_token, expires_in = self._get_oauth_token()
                # Set expiry with 5-minute buffer
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 300)
            else:  # jwt
                jwt_token = self._create_jwt()
                self.access_token = self._exchange_jwt_for_token(jwt_token)
                self.token_expiry = datetime.now() + timedelta(hours=23, minutes=30)

            # Cache token
            self._cache_token()
            print(f"✓ New token generated (expires: {self.token_expiry})")

            return self.access_token

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get access token: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error during authentication: {e}")

    def _get_oauth_token(self):
        """Get access token using OAuth Server-to-Server

        Returns:
            tuple: (access_token, expires_in)

        Raises:
            ValueError: If required OAuth config is missing
            requests.exceptions.RequestException: If API call fails
        """
        required_fields = ['client_id', 'client_secret']
        missing = [f for f in required_fields if f not in self.config]
        if missing:
            raise ValueError(f"Missing required OAuth config fields: {missing}")

        scopes = self.config.get('scopes', [
            'openid',
            'AdobeID',
            'read_organizations',
            'additional_info.projectedProductContext',
            'session'
        ])

        data = {
            'grant_type': 'client_credentials',
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
            'scope': ','.join(scopes) if isinstance(scopes, list) else scopes
        }

        response = requests.post(self.TOKEN_URL_OAUTH, data=data)
        response.raise_for_status()

        result = response.json()
        return result['access_token'], result['expires_in']
    
    def _create_jwt(self):
        """Create JWT token for Adobe IMS (legacy authentication)

        Returns:
            str: Encoded JWT token

        Raises:
            ValueError: If required JWT config is missing
            FileNotFoundError: If private key file not found
        """
        required_fields = ['org_id', 'technical_account_id', 'client_id', 'private_key_path']
        missing = [f for f in required_fields if f not in self.config]
        if missing:
            raise ValueError(f"Missing required JWT config fields: {missing}")

        payload = {
            'exp': int(time.time()) + 60 * 60 * 24,  # 24 hours
            'iss': self.config['org_id'],
            'sub': self.config['technical_account_id'],
            'aud': f"https://ims-na1.adobelogin.com/c/{self.config['client_id']}",
            'https://ims-na1.adobelogin.com/s/ent_dataservices_sdk': True
        }

        # Load private key
        private_key_path = self.config['private_key_path']
        if not os.path.exists(private_key_path):
            raise FileNotFoundError(f"Private key file not found: {private_key_path}")

        try:
            with open(private_key_path, 'r') as f:
                private_key = f.read()
        except Exception as e:
            raise Exception(f"Failed to read private key: {e}")

        # Sign JWT
        try:
            encoded_jwt = jwt.encode(payload, private_key, algorithm='RS256')
            return encoded_jwt
        except Exception as e:
            raise Exception(f"Failed to encode JWT: {e}")
    
    def _exchange_jwt_for_token(self, jwt_token):
        """Exchange JWT for access token (legacy authentication)

        Args:
            jwt_token: Encoded JWT token

        Returns:
            str: Access token

        Raises:
            ValueError: If required config is missing
            requests.exceptions.RequestException: If API call fails
        """
        if 'client_secret' not in self.config:
            raise ValueError("Missing required field: client_secret")

        data = {
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
            'jwt_token': jwt_token
        }

        response = requests.post(self.TOKEN_URL_JWT, data=data)
        response.raise_for_status()

        return response.json()['access_token']
    
    def _is_token_valid(self):
        """Check if cached token is still valid

        Returns:
            bool: True if cached token is valid, False otherwise
        """
        if not self.token_cache_path.exists():
            return False

        try:
            with open(self.token_cache_path, 'r') as f:
                cache = json.load(f)

            expiry = datetime.fromisoformat(cache['expiry'])
            if datetime.now() >= expiry:
                return False

            self.access_token = cache['token']
            self.token_expiry = expiry
            return True

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"⚠️  Warning: Invalid token cache, will regenerate: {e}", file=sys.stderr)
            return False

    def _cache_token(self):
        """Save token to cache file with secure permissions"""
        cache = {
            'token': self.access_token,
            'expiry': self.token_expiry.isoformat(),
            'auth_method': self.auth_method
        }

        try:
            # Create cache file with restricted permissions (owner read/write only)
            self.token_cache_path.touch(mode=0o600, exist_ok=True)

            with open(self.token_cache_path, 'w') as f:
                json.dump(cache, f)

        except Exception as e:
            print(f"⚠️  Warning: Failed to cache token: {e}", file=sys.stderr)

# CLI Interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='AEP Authentication Helper')
    parser.add_argument('--config', required=True, help='Path to config JSON')
    parser.add_argument('--output', help='Output token to file')
    args = parser.parse_args()
    
    auth = AEPAuthHelper(args.config)
    token = auth.get_access_token()
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(token)
        print(f"✓ Token saved to {args.output}")
    else:
        print(f"\nAccess Token:\n{token}")