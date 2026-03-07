import os
import json
from datetime import datetime

# Simple file-based storage
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PAYMENTS_FILE = os.path.join(DATA_DIR, "payments.json")

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize empty files if they don't exist
for file in [USERS_FILE, PAYMENTS_FILE]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({}, f)

def load_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_data(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

async def get_db():
    """Simple context manager for file-based storage"""
    class SimpleDB:
        def __init__(self):
            self.users = load_data(USERS_FILE)
            self.payments = load_data(PAYMENTS_FILE)
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            save_data(USERS_FILE, self.users)
            save_data(PAYMENTS_FILE, self.payments)
    
    return SimpleDB()
