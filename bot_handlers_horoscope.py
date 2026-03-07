from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from bot_services_horoscope_provider import get_today_horoscope, get_weekly_horoscope
from bot_database import get_db
from bot_utils_helpers import get_user, check_rate_limit, is_premium

async def get_horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_gen = get_db()
    db = await db_gen.__anext__()
    user = await get_user(db, user_id)

    if not user or not user.sign:
        await update.message.reply_text("Please set your sign first using /start.")
        await db_gen.aclose()
        return

    # Check premium for detailed version
    premium = await is_premium(user_id)
    sign_name = get_sign_name(user.sign)

    if premium:
        # Detailed premium horoscope
        detailed = await get_today_horoscope(sign_name, detailed=True)
        text = (
            f"🌟 **{sign_name} – Detailed Horoscope**\n"
            f"📅 {datetime.now().strftime('%B %d, %Y')}\n\n"
            f"{detailed}"
        )
    else:
        # Basic free horoscope
        if not await check_rate_limit(user_id, "daily"):
            await update.message.reply_text(
                "You've used your daily free horoscope. Upgrade to premium for unlimited access!\n/premium"
            )
            await db_gen.aclose()
            return
        basic = await get_today_horoscope(sign_name, detailed=False)
        text = f"✨ **{sign_name} – Today's Horoscope**\n\n{basic}\n\n_Upgrade to premium for love, career & health details._"

    await update.message.reply_markdown(text)
    await db_gen.aclose()

async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_gen = get_db()
    db = await db_gen.__anext__()
    user = await get_user(db, user_id)

    if not user or not user.sign:
        await update.message.reply_text("Please set your sign first using /start.")
        await db_gen.aclose()
        return

    premium = await is_premium(user_id)
    sign_name = get_sign_name(user.sign)

    if premium:
        weekly_text = await get_weekly_horoscope(sign_name, detailed=True)
    else:
        if not await check_rate_limit(user_id, "weekly", limit=2):
            await update.message.reply_text("Free weekly limit reached. Upgrade for unlimited weekly forecasts!")
            await db_gen.aclose()
            return
        weekly_text = await get_weekly_horoscope(sign_name, detailed=False)

    await update.message.reply_markdown(weekly_text)
    await db_gen.aclose()

def get_sign_name(sign_num: int) -> str:
    signs = ["aries", "taurus", "gemini", "cancer", "leo", "virgo",
             "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
    return signs[sign_num-1]