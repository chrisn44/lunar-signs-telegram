from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from bot_services_professional_api import get_api
from bot_database import get_db
from bot_utils_helpers import check_rate_limit, is_premium
import random

api = get_api()

# Rich content for premium users (enhances the API response)
LOVE_INSIGHTS = [
    "Venus aligns favorably with your sign today, bringing warmth to your relationships.",
    "Your emotional intelligence is heightened – perfect for deep conversations.",
    "Single? A chance encounter could lead to something special. Be open to new connections.",
    "In relationships, honesty will strengthen your bond today.",
    "Romantic opportunities arise unexpectedly. Trust your intuition.",
    "Your charm is irresistible today – use it wisely!",
    "Past relationship patterns may resurface for healing.",
    "A partner may need extra attention and care today."
]

CAREER_INSIGHTS = [
    "Professional opportunities emerge when you least expect them.",
    "Your leadership skills are highlighted – take initiative on projects.",
    "Collaboration brings better results than working alone today.",
    "A creative idea could lead to professional recognition.",
    "Networking proves valuable – connect with colleagues.",
    "Financial matters require attention – review your budget.",
    "A mentor or guide may offer valuable advice.",
    "Trust your expertise when making work decisions."
]

HEALTH_INSIGHTS = [
    "Energy levels are high – channel them into physical activity.",
    "Focus on hydration and rest to maintain balance.",
    "Mental clarity improves with meditation or quiet time.",
    "Listen to your body's signals – rest when needed.",
    "A new wellness routine could be beneficial.",
    "Stress management should be a priority today.",
    "Outdoor activities will boost your mood and vitality.",
    "Pay attention to your diet – nourishing foods support your energy."
]

COLORS = ["Red", "Blue", "Green", "Yellow", "Purple", "Orange", "Silver", "Gold", "Turquoise", "Pink"]
MOODS = ["Energetic", "Reflective", "Optimistic", "Calm", "Passionate", "Curious", "Grounded", "Inspired"]

def get_sign_name(sign_num: int) -> str:
    """Convert sign number to name"""
    signs = ["aries", "taurus", "gemini", "cancer", "leo", "virgo",
             "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
    return signs[sign_num-1]

def get_element(sign: str) -> str:
    """Get element for a sign"""
    elements = {
        "aries": "fire", "leo": "fire", "sagittarius": "fire",
        "taurus": "earth", "virgo": "earth", "capricorn": "earth",
        "gemini": "air", "libra": "air", "aquarius": "air",
        "cancer": "water", "scorpio": "water", "pisces": "water"
    }
    return elements.get(sign.lower(), "air")

def format_lucky_numbers(numbers):
    """Format lucky numbers list"""
    if isinstance(numbers, list):
        return ', '.join(map(str, numbers))
    return str(numbers)

async def get_horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get daily horoscope from real API"""
    try:
        user_id = update.effective_user.id
        db = await get_db()
        user = db.get_user(user_id)

        if not user or not user.get('sign'):
            await update.message.reply_text(
                "🌙 Please set your zodiac sign first using /start"
            )
            return

        sign_num = user.get('sign')
        sign_name = get_sign_name(sign_num)
        element = get_element(sign_name)
        
        # Check if user is premium
        premium = await is_premium(user_id)
        
        # Send typing action while we fetch
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Call real API
        horoscope_data = await api.get_daily_horoscope(sign_name)
        
        today = datetime.now().strftime("%B %d, %Y")
        
        if premium:
            # PREMIUM: Enhanced horoscope with API data + additional insights
            if horoscope_data and isinstance(horoscope_data, dict):
                # Extract API data
                api_horoscope = horoscope_data.get('horoscope', '')
                lucky_numbers = horoscope_data.get('luckynumbers', [random.randint(1, 9), random.randint(1, 9), random.randint(1, 9)])
                lucky_color = horoscope_data.get('luckycolor', random.choice(COLORS))
                
                # Add premium insights
                love = random.choice(LOVE_INSIGHTS)
                career = random.choice(CAREER_INSIGHTS)
                health = random.choice(HEALTH_INSIGHTS)
                mood = random.choice(MOODS)
                
                text = (
                    f"🌟 **{sign_name.title()} – Premium Horoscope**\n"
                    f"📅 {today}\n\n"
                    f"**Cosmic Overview:**\n{api_horoscope}\n\n"
                    f"❤️ **Love & Relationships:**\n{love}\n\n"
                    f"💼 **Career & Finance:**\n{career}\n\n"
                    f"🏥 **Health & Wellness:**\n{health}\n\n"
                    f"🎨 **Lucky Color:** {lucky_color}\n"
                    f"🔢 **Lucky Numbers:** {format_lucky_numbers(lucky_numbers)}\n"
                    f"😊 **Today's Mood:** {mood}\n"
                    f"🔥 **Element:** {element.title()}"
                )
            else:
                # Fallback if API fails
                text = (
                    f"🌟 **{sign_name.title()} – Premium Horoscope**\n"
                    f"📅 {today}\n\n"
                    f"The cosmic energies bring opportunities for growth and self-discovery.\n\n"
                    f"❤️ **Love:** {random.choice(LOVE_INSIGHTS)}\n\n"
                    f"💼 **Career:** {random.choice(CAREER_INSIGHTS)}\n\n"
                    f"🏥 **Health:** {random.choice(HEALTH_INSIGHTS)}\n\n"
                    f"🎨 **Color:** {random.choice(COLORS)}\n"
                    f"🔢 **Lucky Number:** {random.randint(1, 9)}\n"
                    f"😊 **Mood:** {random.choice(MOODS)}"
                )
        else:
            # FREE: Basic horoscope from API only
            if horoscope_data and isinstance(horoscope_data, dict):
                api_horoscope = horoscope_data.get('horoscope', '')
                lucky_numbers = horoscope_data.get('luckynumbers', [])
                lucky_color = horoscope_data.get('luckycolor', '')
                
                text = (
                    f"✨ **{sign_name.title()} – Daily Horoscope**\n"
                    f"📅 {today}\n\n"
                    f"{api_horoscope}\n"
                )
                
                # Add lucky info if available
                if lucky_numbers:
                    text += f"\n🔢 **Lucky Numbers:** {format_lucky_numbers(lucky_numbers)}"
                if lucky_color:
                    text += f"\n🎨 **Lucky Color:** {lucky_color}"
                
                text += "\n\n_✨ Upgrade to premium for love, career & health insights!_\n"
                text += "_Use /premium to learn more._"
            else:
                # Fallback if API fails
                text = (
                    f"✨ **{sign_name.title()} – Daily Horoscope**\n"
                    f"📅 {today}\n\n"
                    f"The stars are aligning in your favor today. Stay open to opportunities and trust your intuition.\n\n"
                    f"_Upgrade to premium for detailed insights!_"
                )

        await update.message.reply_markdown(text)
        
    except Exception as e:
        print(f"❌ Error in get_horoscope: {e}")
        await update.message.reply_text(
            "🌙 The cosmic energies are shifting... please try again in a moment."
        )

# ⚠️ WEEKLY COMMAND REMOVED - No longer available
# The API doesn't provide weekly forecasts and we don't want repetitive content
