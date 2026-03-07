from sqlalchemy import select
from bot_models import User
from bot_middleware_ratelimit import RateLimiter
from bot_database import get_db
from datetime import datetime

rate_limiter = RateLimiter()

async def get_user(db, telegram_id: int):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()

async def check_rate_limit(user_id: int, action: str = "default", limit: int = None) -> bool:
    if await is_premium(user_id):
        return True
    return await rate_limiter.check_limit(user_id, action)

async def is_premium(user_id: int) -> bool:
    db_gen = get_db()
    db = await db_gen.__anext__()
    user = await get_user(db, user_id)
    await db_gen.aclose()
    if user and user.is_premium and user.premium_until and user.premium_until > datetime.utcnow():
        return True
    return False