from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from bot_services_horoscope_provider import get_today_horoscope, get_weekly_horoscope
from bot_database import get_db
from bot_utils_helpers import check_rate_limit, is_premium

async def get_horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Send debug message
        await update.message.reply_text("🔍 Debug: Starting horoscope function...")
        
        user_id = update.effective_user.id
        await update.message.reply_text(f"🔍 Debug: User ID: {user_id}")
        
        # Get database
        try:
            db = await get_db()
            await update.message.reply_text("✅ Debug: Database connected")
        except Exception as e:
            await update.message.reply_text(f"❌ Debug: Database error: {str(e)}")
            return
        
        # Get user
        try:
            user = db.get_user(user_id)
            await update.message.reply_text(f"✅ Debug: User found: {user is not None}")
        except Exception as e:
            await update.message.reply_text(f"❌ Debug: Get user error: {str(e)}")
            return

        if not user or not user.get('sign'):
            await update.message.reply_text("Please set your sign first using /start.")
            return

        # Check premium
        try:
            premium = await is_premium(user_id)
            await update.message.reply_text(f"✅ Debug: Premium status: {premium}")
        except Exception as e:
            await update.message.reply_text(f"❌ Debug: Premium check error: {str(e)}")
            return

        sign_num = user.get('sign')
        sign_name = get_sign_name(sign_num)
        await update.message.reply_text(f"✅ Debug: Sign: {sign_name}")

        if premium:
            # Detailed premium horoscope
            try:
                detailed = await get_today_horoscope(sign_name, detailed=True)
                await update.message.reply_text(f"✅ Debug: Got premium horoscope")
                text = (
                    f"🌟 **{sign_name.title()} – Detailed Horoscope**\n"
                    f"📅 {datetime.now().strftime('%B %d, %Y')}\n\n"
                    f"{detailed}"
                )
            except Exception as e:
                await update.message.reply_text(f"❌ Debug: Premium horoscope error: {str(e)}")
                return
        else:
            # Basic free horoscope
            try:
                if not await check_rate_limit(user_id, "daily"):
                    await update.message.reply_text(
                        "You've used your daily free horoscope. Upgrade to premium for unlimited access!\n/premium"
                    )
                    return
                await update.message.reply_text(f"✅ Debug: Rate limit passed")
            except Exception as e:
                await update.message.reply_text(f"❌ Debug: Rate limit error: {str(e)}")
                return
                
            try:
                basic = await get_today_horoscope(sign_name, detailed=False)
                await update.message.reply_text(f"✅ Debug: Got basic horoscope")
                text = f"✨ **{sign_name.title()} – Today's Horoscope**\n\n{basic}\n\n_Upgrade to premium for love, career & health details._"
            except Exception as e:
                await update.message.reply_text(f"❌ Debug: Basic horoscope error: {str(e)}")
                return

        # Send final message
        try:
            await update.message.reply_markdown(text)
            await update.message.reply_text("✅ Debug: Message sent successfully!")
        except Exception as e:
            await update.message.reply_text(f"❌ Debug: Send message error: {str(e)}")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Debug: Unexpected error: {str(e)}")
        # Print to logs
        import traceback
        traceback.print_exc()

async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        db = await get_db()
        user = db.get_user(user_id)

        if not user or not user.get('sign'):
            await update.message.reply_text("Please set your sign first using /start.")
            return

        premium = await is_premium(user_id)
        sign_num = user.get('sign')
        sign_name = get_sign_name(sign_num)

        if premium:
            weekly_text = await get_weekly_horoscope(sign_name, detailed=True)
        else:
            if not await check_rate_limit(user_id, "weekly", limit=2):
                await update.message.reply_text("Free weekly limit reached. Upgrade for unlimited weekly forecasts!")
                return
            weekly_text = await get_weekly_horoscope(sign_name, detailed=False)

        await update.message.reply_markdown(weekly_text)
        
    except Exception as e:
        print(f"Error in weekly: {e}")
        await update.message.reply_text(
            "Your weekly forecast is being prepared. Please try again in a moment."
        )

def get_sign_name(sign_num: int) -> str:
    signs = ["aries", "taurus", "gemini", "cancer", "leo", "virgo",
             "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
    return signs[sign_num-1]
