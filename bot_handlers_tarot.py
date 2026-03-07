import random
from telegram import Update
from telegram.ext import ContextTypes
from bot_services_professional_api import get_api
from bot_utils_helpers import is_premium

api = get_api()

async def daily_tarot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Free: one random card with real meaning."""
    try:
        card_data = await api.get_random_tarot_card()
        if not card_data:
            await update.message.reply_text("The cards are shuffling... please try again.")
            return
        
        card_name = list(card_data.keys())[0]
        card_info = card_data[card_name]
        
        # Format card name nicely
        display_name = card_name.replace("_", " ").title()
        
        # Randomly decide upright/reversed (real decks have both)
        reversed = random.random() < 0.3
        orientation = "↕️ Reversed" if reversed else "⬆️ Upright"
        meaning = card_info.get("reversed" if reversed else "upright", "")
        
        await update.message.reply_markdown(
            f"🃏 **Your Real Tarot Card: {display_name}**\n"
            f"{orientation}\n\n"
            f"{meaning}\n\n"
            f"_From the authentic Rider-Waite deck_"
        )
    except Exception as e:
        print(f"Error in daily_tarot: {e}")
        await update.message.reply_text("The cards are not ready. Please try again later.")

async def three_card_spread(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Premium: past-present-future spread with real cards."""
    try:
        user_id = update.effective_user.id
        if not await is_premium(user_id):
            await update.message.reply_markdown(
                "🔮 This is a **premium feature**.\n"
                "Upgrade with /buyweek (50⭐) or /buymonth (150⭐) to unlock all tarot spreads."
            )
            return

        question = " ".join(context.args) if context.args else "General guidance"
        
        # Draw three random cards
        cards = []
        for _ in range(3):
            card_data = await api.get_random_tarot_card()
            if card_data:
                cards.append(card_data)
            await asyncio.sleep(0.5)  # Avoid rate limits
        
        if len(cards) < 3:
            await update.message.reply_text("Unable to draw all cards. Please try again.")
            return
        
        positions = ["Past", "Present", "Future"]
        text = f"**🔮 Three‑Card Spread**\n*Question:* {question}\n\n"
        
        for i, card in enumerate(cards):
            card_name = list(card.keys())[0]
            card_info = card[card_name]
            display_name = card_name.replace("_", " ").title()
            reversed = random.random() < 0.3
            orientation = "↕️ Reversed" if reversed else "⬆️ Upright"
            meaning = card_info.get("reversed" if reversed else "upright", "")
            text += f"**{positions[i]}:** {display_name} {orientation}\n{meaning}\n\n"
        
        await update.message.reply_markdown(text)
    except Exception as e:
        print(f"Error in three_card_spread: {e}")
        await update.message.reply_text("Unable to generate spread. Please try again.")

async def celtic_cross(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Premium: full 10-card Celtic Cross."""
    # Similar to three-card but with 10 cards and positions
    # You can implement similarly
    pass
