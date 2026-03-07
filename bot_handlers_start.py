from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot_database import get_db

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        db = await get_db()

        # Get or create user
        user_data = db.get_user(user.id)
        if not user_data:
            user_data = db.create_user(user.id, user.username)

        if user_data.get('sign'):
            sign_name = ZODIAC_SIGNS[user_data['sign']-1]
            await update.message.reply_text(
                f"✨ Welcome back, {user.first_name}!\n"
                f"Your sign is **{sign_name}**.\n\n"
                "Use /horoscope for today's stars, /tarot for a card, or /premium to unlock more.",
                parse_mode='Markdown'
            )
        else:
            # Sign selection keyboard
            keyboard = []
            for i, sign in enumerate(ZODIAC_SIGNS):
                keyboard.append([InlineKeyboardButton(sign, callback_data=f"set_sign_{i+1}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "🌙 Welcome to LunarSignsBot!\n\nPlease select your zodiac sign:",
                reply_markup=reply_markup
            )
    except Exception as e:
        print(f"Error in start: {e}")
        await update.message.reply_text("Welcome to LunarSignsBot! Please try again in a moment.")

async def set_sign_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        data = query.data
        if data.startswith("set_sign_"):
            sign = int(data.split("_")[2])
            db = await get_db()
            db.update_user(update.effective_user.id, sign=sign)
            await query.edit_message_text(
                f"Great! Your sign is set to **{ZODIAC_SIGNS[sign-1]}**.\n\n"
                "Now you can use /horoscope to see what the stars have in store.",
                parse_mode='Markdown'
            )
    except Exception as e:
        print(f"Error in set_sign_callback: {e}")
        await query.edit_message_text("Sorry, there was an error setting your sign. Please try again.")
