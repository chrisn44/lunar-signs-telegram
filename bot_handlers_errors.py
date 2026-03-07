import logging
import traceback
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors and notify user if appropriate."""
    # Log the error with traceback
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Print full traceback to console
    traceback.print_exc()
    
    # Try to send error details to the user (for debugging)
    try:
        if update and update.effective_message:
            error_msg = str(context.error)
            await update.effective_message.reply_text(
                f"❌ Error: {error_msg}\n\nPlease report this to the admin."
            )
    except:
        pass
