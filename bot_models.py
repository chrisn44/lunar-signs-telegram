# This file is now just for type hints and compatibility
# All actual data is stored in JSON files via bot_database.py

from typing import Optional, Dict, Any
from datetime import datetime

# These are just type hints - actual data comes from JSON
class User:
    """User model - for type hints only"""
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id')
        self.telegram_id = data.get('telegram_id')
        self.username = data.get('username')
        self.sign = data.get('sign')
        self.created_at = data.get('created_at')
        self.is_premium = data.get('is_premium', False)
        self.premium_until = data.get('premium_until')
        self.language = data.get('language', 'en')
        self.captcha_passed = data.get('captcha_passed', False)

class Payment:
    """Payment model - for type hints only"""
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.telegram_payment_id = data.get('telegram_payment_id')
        self.stars_amount = data.get('stars_amount')
        self.purchased_item = data.get('purchased_item')
        self.created_at = data.get('created_at')
