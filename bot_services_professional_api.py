import httpx
import os
import json
from typing import Optional, Dict, List, Any
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
    
    async def get_daily_horoscope(self, sign: str) -> Optional[str]:
        """
        Get today's horoscope text from Zodii API.
        Endpoint: GET /api/horoscope/{sign}
        Returns: String containing the horoscope text
        """
        if not self.token:
            print("❌ ZODII_TOKEN not set in environment variables")
            return None
        
        # Check cache for today
        today = datetime.now().strftime("%Y-%m-%d")
        cache_key = f"horoscope_{sign}_{today}"
        
        if cache_key in self.cache:
            print(f"✅ Using cached horoscope for {sign}")
            return self.cache[cache_key]
        
        # Call API
        url = f"{self.base_url}/api/horoscope/{sign.lower()}"
        
        async with httpx.AsyncClient() as client:
            try:
                print(f"📡 Calling Zodii API: {url}")
                response = await client.get(
                    url,
                    headers=self._get_auth_headers(),
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Handle different response formats
                    if isinstance(data, str):
                        # Direct string response
                        horoscope_text = data
                    elif isinstance(data, dict):
                        # Try common field names for horoscope text
                        horoscope_text = (data.get('horoscope') or 
                                        data.get('description') or 
                                        data.get('message') or 
                                        data.get('text') or
                                        json.dumps(data))
                    else:
                        horoscope_text = str(data)
                    
                    print(f"✅ Received horoscope for {sign} (length: {len(horoscope_text)})")
                    
                    # Cache the result
                    self.cache[cache_key] = horoscope_text
                    return horoscope_text
                    
                elif response.status_code == 401:
                    print(f"❌ Unauthorized - Check your ZODII_TOKEN")
                    return None
                elif response.status_code == 404:
                    print(f"❌ Endpoint not found: {url}")
                    return None
                else:
                    print(f"❌ Zodii API error: {response.status_code}")
                    print(f"Response: {response.text[:200]}")
                    return None
                    
            except Exception as e:
                print(f"❌ Error calling Zodii API: {e}")
                return None
    
    async def get_zodiac_info(self, sign: str) -> Optional[Dict]:
        """
        Get detailed zodiac sign information
        Endpoint: GET /api/zodiac/{sign_name}
        """
        url = f"{self.base_url}/api/zodiac/{sign.lower()}"
        
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
                print(f"❌ Error fetching zodiac info: {e}")
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
                print(f"❌ Error fetching tarot cards: {e}")
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
                print(f"❌ Error drawing tarot cards: {e}")
                return None

# Singleton instance
_api_instance = None

def get_api() -> ProfessionalAstrologyAPI:
    global _api_instance
    if _api_instance is None:
        _api_instance = ProfessionalAstrologyAPI()
    return _api_instance
