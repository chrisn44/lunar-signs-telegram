import json
import random
from telegram import Update
from telegram.ext import ContextTypes
from bot_database import get_db
from bot_utils_helpers import get_user, is_premium

# Load tarot card data
with open("tarot_cards.json", "r", encoding="utf-8") as f:
    TAROT_CARDS = json.load(f)

async def daily_tarot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Free: one random card with brief meaning."""
    user_id = update.effective_user.id
    db_gen = get_db()
    db = await db_gen.__anext__()
    user = await get_user(db, user_id)

    # Pick a random card
    card = random.choice(TAROT_CARDS)
    text = (
        f"🃏 **Your Daily Tarot Card**\n\n"
        f"**{card['name']}**\n"
        f"{card['meaning']['brief']}\n\n"
        f"_For deeper spreads, go premium with /spread_"
    )
    await update.message.reply_markdown(text)
    await db_gen.aclose()

async def three_card_spread(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Premium: past-present-future spread."""
    user_id = update.effective_user.id
    if not await is_premium(user_id):
        await update.message.reply_markdown(
            "🔮 This is a **premium feature**.\n"
            "Upgrade with /buy_week (50⭐) or /buy_month (150⭐) to unlock all tarot spreads."
        )
        return

    # Draw three cards
    cards = random.sample(TAROT_CARDS, 3)
    positions = ["Past", "Present", "Future"]
    text = "**🔮 Three-Card Spread**\n\n"
    for i, card in enumerate(cards):
        text += f"*{positions[i]}:* **{card['name']}**\n"
        text += f"_{card['meaning']['detailed']}_\n\n"

    await update.message.reply_markdown(text)

async def celtic_cross(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Premium: full 10-card Celtic Cross."""
    user_id = update.effective_user.id
    if not await is_premium(user_id):
        await update.message.reply_markdown(
            "🔮 This is a **premium feature**.\n"
            "Upgrade with /buy_week (50⭐) or /buy_month (150⭐) to unlock all tarot spreads."
        )
        return

    # For brevity, we'll just show a placeholder; in real bot you'd implement the full spread.
    cards = random.sample(TAROT_CARDS, 10)
    positions = [
        "The Present", "The Challenge", "Past Foundation", "Near Future",
        "Above (Goal)", "Below (Subconscious)", "Advice", "External Influences",
        "Hopes & Fears", "Final Outcome"
    ]
    text = "**🔮 Celtic Cross Spread**\n\n"
    for i, card in enumerate(cards[:5]):  # show first 5 for demo
        text += f"*{positions[i]}:* **{card['name']}**\n"

    text += "\n_Purchase premium to see the full 10-card interpretation._"
    await update.message.reply_markdown(text)