import os
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List

# Simple file-based storage
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PAYMENTS_FILE = os.path.join(DATA_DIR, "payments.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize files if they don't exist
for file in [USERS_FILE, PAYMENTS_FILE]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump([], f)

def load_data(file_path: str) -> list:
    """Load data from JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except:
        return []

def save_data(file_path: str, data: list):
    """Save data to JSON file"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

class Database:
    """Simple database class for file operations"""
    
    def __init__(self):
        self.users = load_data(USERS_FILE)
        self.payments = load_data(PAYMENTS_FILE)
    
    def save_all(self):
        """Save all data to files"""
        save_data(USERS_FILE, self.users)
        save_data(PAYMENTS_FILE, self.payments)
    
    def get_user(self, telegram_id: int) -> Optional[Dict]:
        """Get user by telegram ID"""
        for user in self.users:
            if user.get('telegram_id') == telegram_id:
                return user
        return None
    
    def create_user(self, telegram_id: int, username: str = None) -> Dict:
        """Create a new user"""
        user = {
            'id': len(self.users) + 1,
            'telegram_id': telegram_id,
            'username': username,
            'sign': None,
            'created_at': datetime.now().isoformat(),
            'is_premium': False,
            'premium_until': None,
            'language': 'en',
            'captcha_passed': False
        }
        self.users.append(user)
        self.save_all()
        return user
    
    def update_user(self, telegram_id: int, **kwargs):
        """Update user fields"""
        user = self.get_user(telegram_id)
        if user:
            for key, value in kwargs.items():
                if value is not None:
                    user[key] = value
            self.save_all()
    
    def add_payment(self, user_id: int, payment_id: str, stars: int, item: str):
        """Record a payment"""
        payment = {
            'id': len(self.payments) + 1,
            'user_id': user_id,
            'telegram_payment_id': payment_id,
            'stars_amount': stars,
            'purchased_item': item,
            'created_at': datetime.now().isoformat()
        }
        self.payments.append(payment)
        self.save_all()

# Database instance
_db_instance = None

async def get_db():
    """Get database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance

async def init_db():
    """Initialize database (just ensures files exist)"""
    global _db_instance
    _db_instance = Database()
    return True
