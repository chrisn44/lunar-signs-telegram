from bot_database import get_db
from bot_middleware_ratelimit import RateLimiter
from datetime import datetime
import dateutil.parser
from bot_config import ADMIN_IDS

rate_limiter = RateLimiter()

async def check_rate_limit(user_id: int, action: str = "default", limit: int = None) -> bool:
    """Check if user is within rate limits."""
    try:
        if await is_premium(user_id):
            return True
        return await rate_limiter.check_limit(user_id, action)
    except Exception as e:
        print(f"Rate limit check error: {e}")
        return True  # Fail open

async def is_premium(user_id: int) -> bool:
    """Check if user has active premium access or is admin."""
    try:
        # Check if user is admin (automatic premium)
        if user_id in ADMIN_IDS:
            print(f"✅ Admin user {user_id} - automatic premium access")
            return True
            
        db = await get_db()
        user_data = db.get_user(user_id)
        if not user_data:
            return False
        if user_data.get('is_premium'):
            premium_until = user_data.get('premium_until')
            if premium_until:
                # Handle both string and datetime objects
                if isinstance(premium_until, str):
                    premium_date = dateutil.parser.parse(premium_until)
                else:
                    premium_date = premium_until
                # Ensure premium_date is timezone-naive for comparison
                if premium_date.tzinfo is not None:
                    premium_date = premium_date.replace(tzinfo=None)
                now = datetime.now()
                if premium_date > now:
                    return True
                else:
                    # Expired, update user record
                    db.update_user(user_id, is_premium=False, premium_until=None)
        return False
    except Exception as e:
        print(f"Error checking premium status: {e}")
        return False
