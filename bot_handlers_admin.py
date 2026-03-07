from telegram import Update
from telegram.ext import ContextTypes
from bot_config import ADMIN_IDS
from bot_database import get_db
from bot_models import User
from sqlalchemy import select

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
        db_gen = get_db()
        db = await db_gen.__anext__()
        total = (await db.execute(select(User))).scalars().all()
        premium = (await db.execute(select(User).where(User.is_premium == True))).scalars().all()
        await update.message.reply_text(
            f"📊 **Bot Statistics**\n"
            f"Total users: {len(total)}\n"
            f"Premium users: {len(premium)}"
        )
        await db_gen.aclose()
    elif command == "broadcast" and len(context.args) > 1:
        message = " ".join(context.args[1:])
        # In production, you'd implement a broadcast job
        await update.message.reply_text(f"Broadcasting: {message}")