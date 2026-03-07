import time
import os

# Simple in-memory rate limiting (no Redis needed)
class RateLimiter:
    def __init__(self):
        # Store rate limits in memory
        self.minute_limits = {}
        self.day_limits = {}
    
    async def check_limit(self, user_id: int, action: str = "default") -> bool:
        """Check if user is within rate limits using in-memory storage."""
        try:
            current_minute = int(time.time() // 60)
            current_day = int(time.time() // 86400)
            
            minute_key = f"{user_id}:{action}:{current_minute}"
            day_key = f"{user_id}:{action}:{current_day}"
            
            # Check minute limit (5 per minute)
            minute_count = self.minute_limits.get(minute_key, 0)
            if minute_count >= 5:
                print(f"Rate limit: Minute limit reached for user {user_id}")
                return False
            
            # Check day limit (20 per day)
            day_count = self.day_limits.get(day_key, 0)
            if day_count >= 20:
                print(f"Rate limit: Day limit reached for user {user_id}")
                return False
            
            # Increment counters
            self.minute_limits[minute_key] = minute_count + 1
            self.day_limits[day_key] = day_count + 1
            
            # Clean up old entries every 100 requests (simple memory management)
            if len(self.minute_limits) > 1000:
                self._cleanup_old_entries()
            
            return True
            
        except Exception as e:
            print(f"Error in rate limiter: {e}")
            # If rate limiter fails, allow the request (fail open)
            return True
    
    def _cleanup_old_entries(self):
        """Remove old entries to prevent memory leaks."""
        try:
            current_minute = int(time.time() // 60)
            current_day = int(time.time() // 86400)
            
            # Remove minute entries older than 10 minutes
            self.minute_limits = {
                k: v for k, v in self.minute_limits.items() 
                if int(k.split(':')[-1]) > current_minute - 10
            }
            
            # Remove day entries older than 2 days
            self.day_limits = {
                k: v for k, v in self.day_limits.items() 
                if int(k.split(':')[-1]) > current_day - 2
            }
        except:
            pass
