from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from bot_services_professional_api import get_api
from bot_database import get_db
from bot_utils_helpers import check_rate_limit, is_premium

api = get_api()

async def get_horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        db = await get_db()
        user = db.get_user(user_id)

        if not user or not user.get('sign'):
            await update.message.reply_text("Please set your sign first using /start.")
            return

        sign_num = user.get('sign')
        sign_name = get_sign_name(sign_num)
        
        # Call real API
        horoscope_data = await api.get_daily_horoscope(sign_name)
        
        if not horoscope_data:
            await update.message.reply_text(
                "The cosmic servers are busy. Please try again in a moment."
            )
            return

        # Check if user is premium
        premium = await is_premium(user_id)

        if premium:
            # Format the real data beautifully
            text = (
                f"🌟 **{sign_name.title()} – Detailed Real Horoscope**\n"
                f"📅 {datetime.now().strftime('%B %d, %Y')}\n\n"
                f"{horoscope_data.get('description', '')}\n\n"
                f"❤️ **Love:** {horoscope_data.get('love', 'Not available')}\n\n"
                f"💼 **Career:** {horoscope_data.get('career', 'Not available')}\n\n"
                f"🏥 **Health:** {horoscope_data.get('health', 'Not available')}\n\n"
                f"🎨 **Color:** {horoscope_data.get('color', 'Unknown')}\n"
                f"🔢 **Lucky Number:** {horoscope_data.get('lucky_number', '?')}\n"
                f"😊 **Mood:** {horoscope_data.get('mood', 'Positive')}"
            )
        else:
            # Free users get only the description (but still real)
            text = (
                f"✨ **{sign_name.title()} – Today's Real Horoscope**\n\n"
                f"{horoscope_data.get('description', '')}\n\n"
                f"_Upgrade to premium for love, career & health details!_"
            )

        await update.message.reply_markdown(text)
        
    except Exception as e:
        print(f"Error in get_horoscope: {e}")
        await update.message.reply_text(
            "The stars are aligning... please try again in a moment."
        )

async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        db = await get_db()
        user = db.get_user(user_id)

        if not user or not user.get('sign'):
            await update.message.reply_text("Please set your sign first using /start.")
            return

        sign_num = user.get('sign')
        sign_name = get_sign_name(sign_num)
        premium = await is_premium(user_id)

        if premium:
            # Get today's horoscope as base
            today_data = await api.get_daily_horoscope(sign_name)
            if today_data:
                text = (
                    f"**{sign_name.title()} – Weekly Preview**\n\n"
                    f"This week's energy is influenced by:\n"
                    f"{today_data.get('description', '')}\n\n"
                    f"Check back daily for your complete horoscope!"
                )
            else:
                text = f"**{sign_name.title()} – Weekly Overview**\n\nCheck back soon!"
            
            await update.message.reply_markdown(text)
        else:
            await update.message.reply_markdown(
                f"**{sign_name.title()} – Weekly Overview**\n\n"
                f"Upgrade to premium for detailed weekly forecasts!\n"
                f"Use /premium to learn more."
            )
    except Exception as e:
        print(f"Error in weekly: {e}")
        await update.message.reply_text("Please try again later.")

def get_sign_name(sign_num: int) -> str:
    signs = ["aries", "taurus", "gemini", "cancer", "leo", "virgo",
             "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
    return signs[sign_num-1]
