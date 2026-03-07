from telegram import Update
from telegram.ext import ContextTypes
from bot_config import ADMIN_IDS
from bot_database import get_db

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Unauthorized.")
        return

    if not context.args:
        await update.message.reply_text(
            "Admin commands:\n"
            "/admin stats - Show bot statistics\n"
            "/admin broadcast <message> - Send to all users"
        )
        return

    command = context.args[0].lower()
    
    if command == "stats":
        try:
            db = await get_db()
            
            # Get all users
            total_users = len(db.users)
            
            # Count premium users
            premium_users = 0
            for user in db.users:
                if user.get('is_premium'):
                    premium_users += 1
            
            await update.message.reply_text(
                f"📊 **Bot Statistics**\n"
                f"Total users: {total_users}\n"
                f"Premium users: {premium_users}\n"
                f"Total payments: {len(db.payments)}",
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Error in admin stats: {e}")
            await update.message.reply_text("Error fetching statistics.")
            
    elif command == "broadcast" and len(context.args) > 1:
        message = " ".join(context.args[1:])
        # In production, you'd implement a broadcast job with rate limiting
        await update.message.reply_text(f"Broadcasting: {message}\n\n(This feature would send to all users in production)")
