import logging
import traceback
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors and notify user if appropriate."""
    # Log the error with traceback
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Print full traceback to console (visible in Railway logs)
    print("=" * 50)
    print("ERROR OCCURRED:")
    traceback.print_exc()
    print("=" * 50)
    
    # Send user-friendly message
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "🌙 An unexpected error occurred. Our team has been notified.\n"
                "Please try again in a moment."
            )
    except:
        pass
