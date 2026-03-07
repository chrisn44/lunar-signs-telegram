import logging
import asyncio
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, PreCheckoutQueryHandler, CallbackQueryHandler
)
from bot_config import BOT_TOKEN, ADMIN_IDS
from bot_handlers_start import start, set_sign_callback
from bot_handlers_horoscope import get_horoscope, weekly
from bot_handlers_tarot import daily_tarot, three_card_spread, celtic_cross
from bot_handlers_premium import (
    info, buy_week, buy_month, compatibility, pre_checkout,
    successful_payment, my_premium
)
from bot_handlers_admin import admin_panel
from bot_handlers_errors import error_handler
from bot_utils_captcha import captcha_required, handle_captcha_answer, reset_captcha
from bot_database import init_db

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Temporary debug handler to see all commands
async def debug_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Debug handler to log all incoming messages."""
    if update.message and update.message.text:
        text = update.message.text
        user_id = update.effective_user.id
        logger.info(f"🔍 DEBUG - Received from user {user_id}: {text}")
        
        # Check if it's a command we should handle
        if text.startswith('/'):
            logger.info(f"🔍 DEBUG - Command detected: {text}")

def main():
    """Main function to start the bot."""
    try:
        # Initialize database
        logger.info("Initializing database...")
        asyncio.get_event_loop().run_until_complete(init_db())
        logger.info("Database initialized successfully")

        # Create application
        logger.info("Creating application...")
        app = Application.builder().token(BOT_TOKEN).build()
        logger.info("Application created successfully")

        # Add debug handler (temporary, can be removed later)
        app.add_handler(MessageHandler(filters.ALL, debug_handler), group=-1)
        logger.info("Debug handler added")

        # Register main handlers
        logger.info("Registering handlers...")
        
        # Basic commands
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("reset", reset_captcha))
        
        # Callback handlers
        app.add_handler(CallbackQueryHandler(set_sign_callback, pattern="^set_sign_"))
        app.add_handler(CallbackQueryHandler(handle_captcha_answer, pattern="^captcha_"))

        # Free commands (with captcha)
        app.add_handler(CommandHandler("horoscope", captcha_required(get_horoscope)))
        app.add_handler(CommandHandler("weekly", captcha_required(weekly)))
        app.add_handler(CommandHandler("tarot", captcha_required(daily_tarot)))

        # Premium commands (check inside handler)
        app.add_handler(CommandHandler("spread", three_card_spread))
        app.add_handler(CommandHandler("celtic", celtic_cross))
        app.add_handler(CommandHandler("compatibility", compatibility))
        app.add_handler(CommandHandler("mypremium", my_premium))

        # Premium info & purchase - support BOTH formats
        app.add_handler(CommandHandler("premium", info))
        app.add_handler(CommandHandler("buy_week", buy_week))
        app.add_handler(CommandHandler("buyweek", buy_week))      # Without underscore
        app.add_handler(CommandHandler("buy_month", buy_month))
        app.add_handler(CommandHandler("buymonth", buy_month))    # Without underscore

        # Admin commands (restricted)
        app.add_handler(CommandHandler("admin", admin_panel, filters=filters.User(user_id=ADMIN_IDS)))

        # Payment handlers - CRITICAL for Stars payments
        app.add_handler(PreCheckoutQueryHandler(pre_checkout))
        app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))

        # Error handler
        app.add_error_handler(error_handler)

        logger.info("All handlers registered successfully")
        logger.info("LunarSignsBot started. Polling...")
        
        # Start polling
        app.run_polling()
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
