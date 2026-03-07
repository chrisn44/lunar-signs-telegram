import httpx
import os
import random
from typing import Optional, Dict

class ProfessionalAstrologyAPI:
    """Real astrological data from professional APIs"""
    
    def __init__(self):
        self.zodii_token = os.getenv("ZODII_TOKEN")
        self.zodii_base = "https://www.zodiiapp.com/api/v1"
        self.free_tarot_base = "https://dajeki.github.io/tarot-api"
    
    async def get_daily_horoscope(self, sign: str) -> Optional[Dict]:
        """
        Get REAL horoscope from Zodii API.
        Returns dict with fields: description, love, career, health, etc.
        """
        if not self.zodii_token:
            print("ZODII_TOKEN not set – using fallback")
            return None
        
        # Zodii uses sign names like "aries", "taurus", etc.
        sign = sign.lower()
        url = f"{self.zodii_base}/zodiac/{sign}/today"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    headers={"Authorization": f"Bearer {self.zodii_token}"},
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    # Parse the response into consistent format
                    return {
                        "description": data.get("description", ""),
                        "love": data.get("love_match", ""),
                        "career": data.get("career", ""),
                        "health": data.get("health", ""),
                        "lucky_number": data.get("lucky_number"),
                        "lucky_color": data.get("lucky_color"),
                        "mood": data.get("mood")
                    }
                else:
                    print(f"Zodii API error: {response.status_code}")
                    return None
            except Exception as e:
                print(f"Error calling Zodii API: {e}")
                return None
    
    async def get_tarot_card(self, card_name: str) -> Optional[Dict]:
        """
        Get REAL tarot card meaning from free API.
        Card name must be in slug format, e.g., "the_fool".
        """
        # Convert "The Fool" to "the_fool"
        slug = card_name.lower().replace(" ", "_")
        url = f"{self.free_tarot_base}/card/major/{slug}.json"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10.0)
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception as e:
                print(f"Error fetching tarot card: {e}")
                return None
    
    async def get_random_tarot_card(self) -> Optional[Dict]:
        """
        Get a random real tarot card from the complete deck.
        """
        # First get the index of all cards
        index_url = f"{self.free_tarot_base}/all.json"
        async with httpx.AsyncClient() as client:
            try:
                index_resp = await client.get(index_url, timeout=10.0)
                if index_resp.status_code == 200:
                    all_data = index_resp.json()
                    cards = list(all_data.get("card", {}).items())
                    if cards:
                        # Randomly select a card
                        card_name, card_data = random.choice(cards)
                        return {card_name: card_data}
                return None
            except Exception as e:
                print(f"Error getting random tarot: {e}")
                return None

# Singleton instance
_api_instance = None

def get_api() -> ProfessionalAstrologyAPI:
    global _api_instance
    if _api_instance is None:
        _api_instance = ProfessionalAstrologyAPI()
    return _api_instance