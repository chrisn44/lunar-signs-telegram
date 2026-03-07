import time
import redis
from bot_config import REDIS_URL, RATE_LIMIT_PER_MINUTE, RATE_LIMIT_PER_DAY

redis_client = redis.from_url(REDIS_URL)

class RateLimiter:
    @staticmethod
    async def check_limit(user_id: int, action: str = "default") -> bool:
        minute_key = f"rate:{user_id}:{action}:minute"
        day_key = f"rate:{user_id}:{action}:day"
        now = int(time.time())
        minute_window = now // 60
        day_window = now // 86400

        minute_count = redis_client.get(f"{minute_key}:{minute_window}")
        if minute_count and int(minute_count) >= RATE_LIMIT_PER_MINUTE:
            return False

        day_count = redis_client.get(f"{day_key}:{day_window}")
        if day_count and int(day_count) >= RATE_LIMIT_PER_DAY:
            return False

        redis_client.incr(f"{minute_key}:{minute_window}")
        redis_client.expire(f"{minute_key}:{minute_window}", 120)
        redis_client.incr(f"{day_key}:{day_window}")
        redis_client.expire(f"{day_key}:{day_window}", 172800)
        return True