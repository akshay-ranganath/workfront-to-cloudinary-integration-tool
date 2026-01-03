"""
Workfront Authentication Module

This module handles authentication with Workfront using OAuth JWT flow.
It generates a JWT token and exchanges it for a session ID that can be used
for Workfront API calls.

Dependencies:
- jwt: For creating JWT tokens
- requests: For HTTP API calls
- python-dotenv: For loading environment variables

Environment Variables Required:
- WORKFRONT_BASE: Base domain for Workfront (e.g., 'example')
- WORKFRONT_CLIENT_ID: OAuth client ID
- WORKFRONT_CLIENT_SECRET: OAuth client secret
- WORKFRONT_CUSTOMER_ID: Customer ID (issuer)
- WORKFRONT_USER_ID: User ID (subject)
- WORKFRONT_PRIVATE_KEY: Private key for JWT signing
"""

import os
import time
import logging
import jwt
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_workfront_session_id() -> str:
    """
    Generate a Workfront OAuth session ID using JWT authentication.
    
    This function creates a JWT token using credentials from environment variables
    and exchanges it for an OAuth session ID from Workfront.
    
    Returns:
        str: Workfront session ID (access token) that can be used for API calls
        
    Raises:
        ValueError: If required environment variables are missing
        requests.HTTPError: If OAuth request fails
    """
    # Retrieve configuration from environment variables
    base = os.getenv('WORKFRONT_BASE')
    client_id = os.getenv('WORKFRONT_CLIENT_ID')
    client_secret = os.getenv('WORKFRONT_CLIENT_SECRET')
    customer_id = os.getenv('WORKFRONT_CUSTOMER_ID')
    user_id = os.getenv('WORKFRONT_USER_ID')
    private_key = os.getenv('WORKFRONT_PRIVATE_KEY')
    
    # Validate that all required variables are present
    required_vars = {
        'WORKFRONT_BASE': base,
        'WORKFRONT_CLIENT_ID': client_id,
        'WORKFRONT_CLIENT_SECRET': client_secret,
        'WORKFRONT_CUSTOMER_ID': customer_id,
        'WORKFRONT_USER_ID': user_id,
        'WORKFRONT_PRIVATE_KEY': private_key
    }
    
    missing_vars = [var_name for var_name, var_value in required_vars.items() if not var_value]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Create JWT token
    logger.debug("Creating JWT token for Workfront authentication")
    now = int(time.time())
    payload = {
        "iss": customer_id,       # issuer
        "sub": user_id,           # subject
        "exp": now + 180          # 3 minutes is typical; keep it short
    }
    jwt_token = jwt.encode(payload, private_key, algorithm="RS256")
    
    # Exchange JWT for access token (sessionID)
    logger.info("Requesting Workfront OAuth session ID")
    try:
        resp = requests.post(
            f"https://{base}.my.workfront.com/integrations/oauth2/api/v1/jwt/exchange",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "jwt_token": jwt_token
            },
            timeout=30
        )
        resp.raise_for_status()
        session_id = resp.json()["access_token"]  # this IS the sessionID
        
        logger.info("✅ Session ID retrieved successfully")
        return session_id
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to authenticate with Workfront: {e}")
        raise

