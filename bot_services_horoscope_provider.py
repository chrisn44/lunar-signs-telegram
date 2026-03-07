import httpx
import random
from bot_config import AZTRO_API_URL

# Fallback horoscopes in case API fails
FALLBACK_HOROSCOPES = {
    "aries": "Today brings exciting opportunities. Trust your instincts and take that leap of faith.",
    "taurus": "Patience will pay off today. Stay grounded and focus on your long-term goals.",
    "gemini": "Your communication skills are highlighted. Perfect day for important conversations.",
    "cancer": "Trust your intuition today. Family matters may need your attention.",
    "leo": "Your confidence shines bright. Take the lead on that project you've been considering.",
    "virgo": "Pay attention to details today. A small discovery could lead to big things.",
    "libra": "Balance is key today. Trust your sense of fairness in all situations.",
    "scorpio": "Your passion is your power. Channel it wisely and watch magic happen.",
    "sagittarius": "Adventure calls! Step out of your comfort zone today.",
    "capricorn": "Hard work pays off. Keep climbing, success is near.",
    "aquarius": "Your unique perspective is needed. Share your ideas freely.",
    "pisces": "Trust your dreams today. They hold important messages for you."
}

async def get_today_horoscope(sign: str, detailed: bool = False) -> str:
    """Fetch today's horoscope from aztro API."""
    async with httpx.AsyncClient() as client:
        try:
            # Make sure sign is lowercase
            sign = sign.lower().strip()
            
            response = await client.post(
                AZTRO_API_URL,
                params={"sign": sign, "day": "today"},
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if detailed:
                    # Build a rich premium horoscope
                    love = data.get('love', 'Good day for romance.')
                    career = data.get('career', 'Professional opportunities arise.')
                    health = data.get('health', 'Take care of yourself today.')
                    color = data.get('color', 'Blue')
                    lucky_number = data.get('lucky_number', '7')
                    mood = data.get('mood', 'Positive')
                    
                    return (
                        f"❤️ **Love:** {love}\n\n"
                        f"💼 **Career:** {career}\n\n"
                        f"🏥 **Health:** {health}\n\n"
                        f"🎨 **Color:** {color}\n"
                        f"🔢 **Lucky Number:** {lucky_number}\n"
                        f"😊 **Mood:** {mood}"
                    )
                else:
                    # Basic horoscope
                    return data.get('description', FALLBACK_HOROSCOPES.get(sign, "The stars are aligned in your favor today!"))
            else:
                # Return fallback if API fails
                return FALLBACK_HOROSCOPES.get(sign, "The stars are aligned in your favor today!")
                
        except Exception as e:
            print(f"Error fetching horoscope: {e}")
            # Return fallback on error
            return FALLBACK_HOROSCOPES.get(sign, "The stars are aligned in your favor today!")

async def get_weekly_horoscope(sign: str, detailed: bool = False) -> str:
    """Generate weekly horoscope."""
    sign = sign.lower().strip()
    
    if detailed:
        return (
            f"**{sign.title()} - Weekly Premium Forecast**\n\n"
            f"**Monday-Wednesday:** Career opportunities arise. Network with colleagues.\n\n"
            f"**Thursday-Friday:** Love and relationships take center stage. Perfect for date night.\n\n"
            f"**Weekend:** Self-care and reflection. Take time for yourself.\n\n"
            f"**Lucky Day:** Friday\n"
            f"**Challenge Day:** Tuesday\n"
            f"**Color of the Week:** Green"
        )
    else:
        return (
            f"**{sign.title()} - Weekly Overview**\n\n"
            f"This week brings growth and opportunities. Trust your journey.\n\n"
            f"_Upgrade to premium for detailed daily breakdowns!_"
        )
