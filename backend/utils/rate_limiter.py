from datetime import datetime, timedelta
from collections import defaultdict
from fastapi import HTTPException
from config.settings import RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_TIME_WINDOW

class RateLimiter:
    def __init__(self, max_requests: int = 30, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
    
    async def check_rate_limit(self, client_ip: str):
        try:
            now = datetime.now()
            
            # Clean old requests
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if now - req_time < timedelta(seconds=self.time_window)
            ]
            
            # Check rate limit
            if len(self.requests[client_ip]) >= self.max_requests:
                raise HTTPException(
                    status_code=429, 
                    detail="Rate limit exceeded. Please try again later."
                )
            
            # Add current request
            self.requests[client_ip].append(now)
        except HTTPException:
            # Re-raise HTTPException as it's an expected flow for rate limiting
            raise
        except Exception as e:
            print(f"Rate limiter error for IP {client_ip}: {e}")
            # For any other unexpected error in rate limiting, raise a generic server error
            raise HTTPException(
                status_code=500,
                detail="An internal error occurred with rate limiting. Please try again later."
            )

# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=RATE_LIMIT_MAX_REQUESTS, time_window=RATE_LIMIT_TIME_WINDOW)

