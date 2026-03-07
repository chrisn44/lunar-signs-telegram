from bot_database import get_db
from bot_middleware_ratelimit import RateLimiter
from datetime import datetime
import dateutil.parser

rate_limiter = RateLimiter()

async def check_rate_limit(user_id: int, action: str = "default", limit: int = None) -> bool:
    """Check if user is within rate limits"""
    try:
        # Premium users bypass rate limits
        if await is_premium(user_id):
            return True
        
        # Check rate limit
        return await rate_limiter.check_limit(user_id, action)
    except Exception as e:
        print(f"Rate limit check error: {e}")
        # If rate limit check fails, allow the request
        return True

async def is_premium(user_id: int) -> bool:
    """Check if user has premium access"""
    try:
        db = await get_db()
        user_data = db.get_user(user_id)
        
        if user_data and user_data.get('is_premium'):
            premium_until = user_data.get('premium_until')
            if premium_until:
                # Parse ISO format date
                if isinstance(premium_until, str):
                    premium_date = dateutil.parser.parse(premium_until)
                    if premium_date > datetime.now():
                        return True
    except Exception as e:
        print(f"Error checking premium status: {e}")
    return False
