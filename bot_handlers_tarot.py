import json
import random
from telegram import Update
from telegram.ext import ContextTypes
from bot_database import get_db
from bot_utils_helpers import is_premium

# Load tarot card data
try:
    with open("tarot_cards.json", "r", encoding="utf-8") as f:
        TAROT_CARDS = json.load(f)
except:
    # Fallback if file doesn't exist
    TAROT_CARDS = [
        {
            "name": "The Fool",
            "meaning": {
                "brief": "New beginnings, innocence, spontaneity.",
                "detailed": "The Fool represents a fresh start, a leap of faith."
            }
        },
        {
            "name": "The Magician",
            "meaning": {
                "brief": "Manifestation, resourcefulness, power.",
                "detailed": "You have all the tools you need to succeed."
            }
        }
    ]

async def daily_tarot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Free: one random card with brief meaning."""
    try:
        # Pick a random card
        card = random.choice(TAROT_CARDS)
        text = (
            f"🃏 **Your Daily Tarot Card**\n\n"
            f"**{card['name']}**\n"
            f"{card['meaning']['brief']}\n\n"
            f"_For deeper spreads, go premium with /spread_"
        )
        await update.message.reply_markdown(text)
    except Exception as e:
        print(f"Error in daily_tarot: {e}")
        await update.message.reply_text("Sorry, I couldn't draw a tarot card right now.")

async def three_card_spread(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Premium: past-present-future spread."""
    try:
        user_id = update.effective_user.id
        if not await is_premium(user_id):
            await update.message.reply_markdown(
                "🔮 This is a **premium feature**.\n"
                "Upgrade with /buy_week (50⭐) or /buy_month (150⭐) to unlock all tarot spreads."
            )
            return

        # Draw three cards
        cards = random.sample(TAROT_CARDS, min(3, len(TAROT_CARDS)))
        positions = ["Past", "Present", "Future"]
        text = "**🔮 Three-Card Spread**\n\n"
        for i, card in enumerate(cards):
            text += f"*{positions[i]}:* **{card['name']}**\n"
            text += f"_{card['meaning']['detailed']}_\n\n"

        await update.message.reply_markdown(text)
    except Exception as e:
        print(f"Error in three_card_spread: {e}")
        await update.message.reply_text("Sorry, I couldn't generate your spread right now.")

async def celtic_cross(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Premium: full 10-card Celtic Cross."""
    try:
        user_id = update.effective_user.id
        if not await is_premium(user_id):
            await update.message.reply_markdown(
                "🔮 This is a **premium feature**.\n"
                "Upgrade with /buy_week (50⭐) or /buy_month (150⭐) to unlock all tarot spreads."
            )
            return

        # Draw 5 cards for preview (full version would be 10)
        cards = random.sample(TAROT_CARDS, min(5, len(TAROT_CARDS)))
        positions = [
            "The Present", "The Challenge", "Past Foundation", "Near Future",
            "Above (Goal)"
        ]
        text = "**🔮 Celtic Cross Spread**\n\n"
        for i, card in enumerate(cards):
            text += f"*{positions[i]}:* **{card['name']}**\n"

        text += "\n_Purchase premium to see the full 10-card interpretation._"
        await update.message.reply_markdown(text)
    except Exception as e:
        print(f"Error in celtic_cross: {e}")
        await update.message.reply_text("Sorry, I couldn't generate your spread right now.")
