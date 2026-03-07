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

        # Check premium for detailed version (but both get real data)
        premium = await is_premium(user_id)
        
        # Call real API
        horoscope_data = await api.get_daily_horoscope(sign_name)
        
        if not horoscope_data:
            # If API fails, use fallback (your existing generator)
            await update.message.reply_text("The cosmic servers are busy. Please try again in a moment.")
            return

        if premium:
            text = (
                f"🌟 **{sign_name.title()} – Detailed Real Horoscope**\n"
                f"📅 {datetime.now().strftime('%B %d, %Y')}\n\n"
                f"{horoscope_data['description']}\n\n"
                f"❤️ **Love:** {horoscope_data['love']}\n\n"
                f"💼 **Career:** {horoscope_data['career']}\n\n"
                f"🏥 **Health:** {horoscope_data['health']}\n\n"
                f"🎨 **Color:** {horoscope_data.get('lucky_color', 'Unknown')}\n"
                f"🔢 **Lucky Number:** {horoscope_data.get('lucky_number', '?')}\n"
                f"😊 **Mood:** {horoscope_data.get('mood', 'Positive')}"
            )
        else:
            # Free users get only the description (but still real)
            text = (
                f"✨ **{sign_name.title()} – Today's Real Horoscope**\n\n"
                f"{horoscope_data['description']}\n\n"
                f"_Upgrade to premium for love, career & health details._"
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

        # For weekly, we could aggregate multiple days or use a separate endpoint.
        # Zodii doesn't have a weekly endpoint; we'll create a simple weekly summary.
        # For premium, we'll generate a more detailed forecast.
        
        if premium:
            # Premium gets a more elaborate weekly forecast (still based on real daily data)
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            weekly_text = f"**{sign_name.title()} – Weekly Premium Forecast**\n\n"
            for day in days:
                day_data = await api.get_daily_horoscope(sign_name)
                if day_data:
                    weekly_text += f"**{day}:** {day_data['description'][:100]}...\n\n"
                await asyncio.sleep(0.5)  # Avoid rate limits
            weekly_text += "**Weekend:** Rest and recharge."
            await update.message.reply_markdown(weekly_text)
        else:
            # Free weekly overview
            await update.message.reply_markdown(
                f"**{sign_name.title()} – Weekly Overview**\n\n"
                f"Upgrade to premium for a detailed day-by-day forecast!\n"
                f"Use /premium to learn more."
            )
    except Exception as e:
        print(f"Error in weekly: {e}")
        await update.message.reply_text("Please try again later.")

def get_sign_name(sign_num: int) -> str:
    signs = ["aries", "taurus", "gemini", "cancer", "leo", "virgo",
             "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
    return signs[sign_num-1]
