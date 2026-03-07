import httpx
import os
import random
from typing import Optional, Dict, List
from datetime import datetime

class ProfessionalAstrologyAPI:
    """Real astrological data from Zodii API"""
    
    def __init__(self):
        self.token = os.getenv("ZODII_TOKEN")
        self.base_url = "https://www.zodiiapp.com"
        self.cache = {}  # Simple cache to save API calls
        self.last_fetch_date = None
    
    def _get_auth_headers(self) -> Dict:
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    async def get_daily_horoscope(self, sign: str) -> Optional[Dict]:
        """
        Get REAL horoscope from Zodii API.
        Endpoint: GET /api/horoscope/{sign}
        """
        if not self.token:
            print("ZODII_TOKEN not set")
            return None
        
        # Check cache for today
        today = datetime.now().strftime("%Y-%m-%d")
        cache_key = f"horoscope_{sign}_{today}"
        
        if cache_key in self.cache:
            print(f"Using cached horoscope for {sign}")
            return self.cache[cache_key]
        
        # Call API
        url = f"{self.base_url}/api/horoscope/{sign.lower()}"
        
        async with httpx.AsyncClient() as client:
            try:
                print(f"Calling Zodii API: {url}")
                response = await client.get(
                    url,
                    headers=self._get_auth_headers(),
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Cache the result
                    self.cache[cache_key] = data
                    return data
                else:
                    print(f"Zodii API error: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
                    
            except Exception as e:
                print(f"Error calling Zodii API: {e}")
                return None
    
    async def get_tarot_cards(self) -> Optional[List]:
        """
        Get all tarot cards
        Endpoint: GET /api/tarot/cards
        """
        url = f"{self.base_url}/api/tarot/cards"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    headers=self._get_auth_headers(),
                    timeout=10.0
                )
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception as e:
                print(f"Error fetching tarot cards: {e}")
                return None
    
    async def draw_tarot_cards(self, count: int = 1, seed: str = None) -> Optional[List]:
        """
        Draw random tarot cards
        Endpoint: POST /api/tarot/draw
        """
        url = f"{self.base_url}/api/tarot/draw"
        
        payload = {"count": count}
        if seed:
            payload["shuffle_seed"] = seed
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    headers=self._get_auth_headers(),
                    json=payload,
                    timeout=10.0
                )
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception as e:
                print(f"Error drawing tarot cards: {e}")
                return None
    
    async def get_compatibility(self, person1: Dict, person2: Dict) -> Optional[Dict]:
        """
        Check compatibility between two people
        Endpoint: POST /api/compatibility
        """
        url = f"{self.base_url}/api/compatibility"
        
        payload = [person1, person2]
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    headers=self._get_auth_headers(),
                    json=payload,
                    timeout=10.0
                )
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception as e:
                print(f"Error checking compatibility: {e}")
                return None

# Singleton instance
_api_instance = None

def get_api() -> ProfessionalAstrologyAPI:
    global _api_instance
    if _api_instance is None:
        _api_instance = ProfessionalAstrologyAPI()
    return _api_instance
