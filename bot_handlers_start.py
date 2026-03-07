from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot_database import get_db
from bot_utils_helpers import get_user

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = await get_db()

    # Get or create user
    db_user = db.get_user(user.id)
    if not db_user:
        db_user = db.create_user(user.id, user.username)

    if db_user.get('sign'):
        sign_name = ZODIAC_SIGNS[db_user['sign']-1]
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

async def set_sign_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
