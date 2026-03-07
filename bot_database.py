import os
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List

# Simple file-based storage
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PAYMENTS_FILE = os.path.join(DATA_DIR, "payments.json")

print(f"📁 Data directory: {DATA_DIR}")
print(f"📄 Users file: {USERS_FILE}")
print(f"📄 Payments file: {PAYMENTS_FILE}")

# Ensure data directory exists
try:
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"✅ Data directory created/verified")
except Exception as e:
    print(f"❌ Error creating data directory: {e}")

# Initialize files if they don't exist
for file_path, file_name in [(USERS_FILE, "users"), (PAYMENTS_FILE, "payments")]:
    if not os.path.exists(file_path):
        try:
            with open(file_path, 'w') as f:
                json.dump([], f)
            print(f"✅ Created {file_name}.json")
        except Exception as e:
            print(f"❌ Error creating {file_name}.json: {e}")

def load_data(file_path: str, file_name: str) -> list:
    """Load data from JSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            print(f"✅ Loaded {len(data)} records from {file_name}.json")
            return data
    except Exception as e:
        print(f"❌ Error loading {file_name}.json: {e}")
        return []

def save_data(file_path: str, file_name: str, data: list):
    """Save data to JSON file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"✅ Saved {len(data)} records to {file_name}.json")
    except Exception as e:
        print(f"❌ Error saving {file_name}.json: {e}")

class Database:
    """Simple database class for file operations"""
    
    def __init__(self):
        print("🔄 Initializing Database...")
        self.users = load_data(USERS_FILE, "users")
        self.payments = load_data(PAYMENTS_FILE, "payments")
        print(f"📊 Database initialized with {len(self.users)} users and {len(self.payments)} payments")
    
    def save_all(self):
        """Save all data to files"""
        print("🔄 Saving all data...")
        save_data(USERS_FILE, "users", self.users)
        save_data(PAYMENTS_FILE, "payments", self.payments)
        print("✅ All data saved")
    
    def get_user(self, telegram_id: int) -> Optional[Dict]:
        """Get user by telegram ID"""
        for user in self.users:
            if user.get('telegram_id') == telegram_id:
                print(f"✅ Found user {telegram_id}: sign={user.get('sign')}, premium={user.get('is_premium')}, captcha={user.get('captcha_passed')}")
                return user
        print(f"❌ User {telegram_id} not found")
        return None
    
    def create_user(self, telegram_id: int, username: str = None) -> Dict:
        """Create a new user"""
        print(f"🔄 Creating new user {telegram_id} with username: {username}")
        
        # Check if user already exists
        existing = self.get_user(telegram_id)
        if existing:
            print(f"⚠️ User {telegram_id} already exists, returning existing")
            return existing
        
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
        print(f"✅ Created new user {telegram_id} with ID {user['id']}")
        return user
    
    def update_user(self, telegram_id: int, **kwargs):
        """Update user fields"""
        print(f"🔄 Updating user {telegram_id} with: {kwargs}")
        user = self.get_user(telegram_id)
        if user:
            for key, value in kwargs.items():
                if value is not None:
                    old_value = user.get(key)
                    user[key] = value
                    print(f"  • Changed {key}: {old_value} -> {value}")
            self.save_all()
            # Verify update
            updated_user = self.get_user(telegram_id)
            print(f"✅ User after update: captcha_passed={updated_user.get('captcha_passed')}, premium={updated_user.get('is_premium')}")
        else:
            print(f"❌ User {telegram_id} not found for update")
            # Create user if not exists
            print(f"🔄 Creating user {telegram_id} since they don't exist")
            self.create_user(telegram_id)
            # Try update again
            self.update_user(telegram_id, **kwargs)
    
    def add_payment(self, user_id: int, payment_id: str, stars: int, item: str):
        """Record a payment"""
        print(f"🔄 Recording payment for user {user_id}: {stars} stars for {item}")
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
        print(f"✅ Payment recorded with ID {payment['id']}")
        
        # Update user premium status if needed
        if item in ['week', 'month']:
            from datetime import datetime, timedelta
            user = self.get_user(user_id)
            if user:
                now = datetime.now()
                if item == 'week':
                    expiry = now + timedelta(days=7)
                else:
                    expiry = now + timedelta(days=30)
                self.update_user(user_id, is_premium=True, premium_until=expiry.isoformat())
                print(f"✅ Updated user {user_id} premium until {expiry.isoformat()}")

# Database instance
_db_instance = None

async def get_db():
    """Get database instance"""
    global _db_instance
    if _db_instance is None:
        print("🔄 Creating new database instance...")
        _db_instance = Database()
        print("✅ Database instance created")
    return _db_instance

async def init_db():
    """Initialize database (just ensures files exist)"""
    global _db_instance
    print("🔄 Initializing database...")
    _db_instance = Database()
    print("✅ Database initialized")
    return True
