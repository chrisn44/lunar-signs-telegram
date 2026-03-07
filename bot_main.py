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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    # Initialize database
    asyncio.get_event_loop().run_until_complete(init_db())

    # Create application
    app = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset_captcha))
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
    app.add_handler(CommandHandler("buyweek", buy_week))      # Added without underscore
    app.add_handler(CommandHandler("buy_month", buy_month))
    app.add_handler(CommandHandler("buymonth", buy_month))    # Added without underscore

    # Admin
    app.add_handler(CommandHandler("admin", admin_panel, filters=filters.User(user_id=ADMIN_IDS)))

    # Payment handlers - CRITICAL for Stars payments
    app.add_handler(PreCheckoutQueryHandler(pre_checkout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))

    # Error handler
    app.add_error_handler(error_handler)

    logger.info("LunarSignsBot started. Polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
