"""
Simple API Key Authentication for AI Guru Multibot
"""
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import hashlib
import hmac
from datetime import datetime, timedelta

security = HTTPBearer()

class APIKeyAuth:
    def __init__(self):
        self.api_keys = {
            # Add your API keys here - generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
            "dev_key": "development_access_key_change_in_production",
            # "prod_key": "your_production_api_key_here"
        }
    
    async def verify_api_key(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Verify API key from Authorization header"""
        if not credentials or not credentials.credentials:
            raise HTTPException(status_code=401, detail="API key required")
        
        api_key = credentials.credentials
        
        # Check if key exists and is valid
        if api_key not in self.api_keys.values():
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        return api_key
    
    def generate_api_key(self, name: str) -> str:
        """Generate a new API key"""
        import secrets
        return f"{name}_{secrets.token_urlsafe(32)}"

# Global auth instance
auth = APIKeyAuth()

# Optional authentication dependency
async def optional_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Optional API key verification - doesn't fail if no key provided"""
    try:
        if credentials and credentials.credentials:
            return await auth.verify_api_key(credentials)
        return None
    except HTTPException:
        return None