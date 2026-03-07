import httpx
import random
from datetime import datetime

# Fallback horoscopes that ALWAYS work
FALLBACK_HOROSCOPES = {
    "aries": {
        "today": "Today brings exciting opportunities for Aries. Your natural leadership skills will shine, and others will look to you for guidance. Trust your instincts and take that leap of faith.",
        "love": "Romantic opportunities arise mid-week. Single? Someone new enters your circle.",
        "career": "Professional recognition comes your way. Don't be shy about showcasing your talents.",
        "health": "High energy levels, but remember to rest when needed."
    },
    "taurus": {
        "today": "Patience will pay off for Taurus today. Stay grounded and focused on your long-term goals. Financial matters look promising.",
        "love": "Deepen existing connections. Quality time with loved ones is highlighted.",
        "career": "Steady progress in work. Your reliability is noticed by superiors.",
        "health": "Focus on nutrition and self-care. Your body needs nourishment."
    },
    "gemini": {
        "today": "Your communication skills are highlighted, Gemini. Perfect day for important conversations, networking, and sharing ideas.",
        "love": "Flirty conversations lead to romantic possibilities. Express your feelings.",
        "career": "Your adaptability is your greatest asset. Embrace change at work.",
        "health": "Mental energy high. Channel it into productive activities."
    },
    "cancer": {
        "today": "Trust your intuition today, Cancer. Family matters may need your attention, and your nurturing nature will be appreciated.",
        "love": "Vulnerability strengthens bonds. Open your heart to loved ones.",
        "career": "Your nurturing nature makes you a valuable team player. Help others succeed.",
        "health": "Emotional health affects physical well-being. Practice self-care."
    },
    "leo": {
        "today": "Your confidence shines bright, Leo. Take the lead on that project you've been considering. Others are ready to follow you.",
        "love": "Romance blossoms. Grand gestures are appreciated.",
        "career": "Leadership opportunities arise. Step up and take charge.",
        "health": "Heart health focus. Cardiovascular exercise beneficial."
    },
    "virgo": {
        "today": "Pay attention to details today, Virgo. A small discovery could lead to big things. Organization brings peace of mind.",
        "love": "Service to others strengthens relationships. Small gestures matter.",
        "career": "Your analytical skills solve complex problems. Recognition follows.",
        "health": "Digestive health focus. Eat mindfully and regularly."
    },
    "libra": {
        "today": "Balance is key today, Libra. Trust your sense of fairness in all situations. Relationships take center stage.",
        "love": "Romantic partnerships flourish. Compromise leads to harmony.",
        "career": "Collaboration brings success. Team up with colleagues.",
        "health": "Balance rest and activity. Your kidneys need hydration."
    },
    "scorpio": {
        "today": "Your passion is your power, Scorpio. Channel it wisely and watch magic happen. Deep conversations reveal truths.",
        "love": "Passionate connections deepen. Vulnerability brings intimacy.",
        "career": "Your determination overcomes obstacles. Keep pushing forward.",
        "health": "Regenerative healing possible. Focus on rest and recovery."
    },
    "sagittarius": {
        "today": "Adventure calls, Sagittarius! Step out of your comfort zone today. New experiences bring valuable lessons.",
        "love": "Exciting romantic possibilities. Be open to unexpected connections.",
        "career": "Travel or education opportunities arise. Say yes to new challenges.",
        "health": "Outdoor activities boost mood and vitality. Get moving."
    },
    "capricorn": {
        "today": "Hard work pays off, Capricorn. Keep climbing, success is near. Your discipline inspires others.",
        "love": "Commitment and loyalty strengthen bonds. Long-term planning benefits relationships.",
        "career": "Professional recognition and advancement. Your efforts are noticed.",
        "health": "Bone and joint health focus. Good posture matters."
    },
    "aquarius": {
        "today": "Your unique perspective is needed, Aquarius. Share your ideas freely. Innovation brings excitement.",
        "love": "Unconventional relationships thrive. Embrace your uniqueness.",
        "career": "Innovative ideas gain traction. Think outside the box.",
        "health": "Circulation and nervous system focus. Stay hydrated."
    },
    "pisces": {
        "today": "Trust your dreams today, Pisces. They hold important messages for you. Your creativity flows freely.",
        "love": "Romantic dreams manifest. Intuition guides your heart.",
        "career": "Creative projects flourish. Your imagination is your asset.",
        "health": "Foot and lymphatic system care. Rest and rejuvenate."
    }
}

async def get_today_horoscope(sign: str, detailed: bool = False) -> str:
    """Get horoscope with guaranteed fallback"""
    sign = sign.lower().strip()
    
    # Try API but don't fail if it doesn't work
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?sign={sign}&day=today")
            if response.status_code == 200:
                data = response.json()
                if "data" in data and "horoscope_data" in data["data"]:
                    api_text = data["data"]["horoscope_data"]
                    
                    if detailed:
                        sign_data = FALLBACK_HOROSCOPES.get(sign, FALLBACK_HOROSCOPES["aries"])
                        return (
                            f"❤️ **Love:** {sign_data['love']}\n\n"
                            f"💼 **Career:** {sign_data['career']}\n\n"
                            f"🏥 **Health:** {sign_data['health']}\n\n"
                            f"📝 **Daily Insight:** {api_text}"
                        )
                    else:
                        return api_text
    except Exception as e:
        print(f"API error (using fallback): {e}")
    
    # Use guaranteed fallback
    sign_data = FALLBACK_HOROSCOPES.get(sign, FALLBACK_HOROSCOPES["aries"])
    
    if detailed:
        return (
            f"❤️ **Love:** {sign_data['love']}\n\n"
            f"💼 **Career:** {sign_data['career']}\n\n"
            f"🏥 **Health:** {sign_data['health']}\n\n"
            f"📝 **Daily Insight:** {sign_data['today']}"
        )
    else:
        return sign_data['today']

async def get_weekly_horoscope(sign: str, detailed: bool = False) -> str:
    """Get weekly horoscope from fallback data"""
    sign = sign.lower().strip()
    sign_data = FALLBACK_HOROSCOPES.get(sign, FALLBACK_HOROSCOPES["aries"])
    
    if detailed:
        return (
            f"**{sign.title()} - Weekly Premium Forecast**\n\n"
            f"**Monday-Wednesday:** {sign_data['career']}\n\n"
            f"**Thursday-Friday:** {sign_data['love']}\n\n"
            f"**Weekend:** {sign_data['health']}\n\n"
            f"**Career Highlight:** {sign_data['career']}\n"
            f"**Wellness Focus:** {sign_data['health']}"
        )
    else:
        return (
            f"**{sign.title()} - Weekly Overview**\n\n"
            f"{sign_data['today'][:100]}...\n\n"
            f"_Upgrade to premium for detailed daily breakdowns!_"
        )
