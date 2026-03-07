import random
from telegram import Update
from telegram.ext import ContextTypes
from bot_services_professional_api import get_api
from bot_utils_helpers import is_premium
import asyncio

api = get_api()

async def daily_tarot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Free: one random card with real meaning."""
    try:
        # Draw one random card from Zodii API
        cards = await api.draw_tarot_cards(count=1)
        
        if not cards or len(cards) == 0:
            await update.message.reply_text("The cards are shuffling... please try again.")
            return
        
        card = cards[0]  # First card from the draw
        
        # Format card info
        card_name = card.get('name', 'Unknown')
        suit = card.get('suit', '')
        rank = card.get('rank', '')
        
        # Get keywords as string
        keywords = card.get('keywords', [])
        keywords_str = ', '.join(keywords) if keywords else ''
        
        await update.message.reply_markdown(
            f"🃏 **Your Real Tarot Card: {card_name}**\n"
            f"{suit} – {rank}\n\n"
            f"**Keywords:** {keywords_str}\n\n"
            f"_From the authentic Rider-Waite deck via Zodii API_"
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
        cards = await api.draw_tarot_cards(count=3)
        
        if not cards or len(cards) < 3:
            await update.message.reply_text("Unable to draw all cards. Please try again.")
            return
        
        positions = ["Past", "Present", "Future"]
        text = f"**🔮 Three‑Card Spread**\n*Question:* {question}\n\n"
        
        for i, card in enumerate(cards[:3]):
            card_name = card.get('name', 'Unknown')
            suit = card.get('suit', '')
            rank = card.get('rank', '')
            keywords = card.get('keywords', [])
            keywords_str = ', '.join(keywords) if keywords else ''
            
            text += f"**{positions[i]}:** {card_name} ({suit} {rank})\n"
            text += f"_{keywords_str}_\n\n"
        
        await update.message.reply_markdown(text)
    except Exception as e:
        print(f"Error in three_card_spread: {e}")
        await update.message.reply_text("Unable to generate spread. Please try again.")

async def celtic_cross(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Premium: full 10-card Celtic Cross."""
    try:
        user_id = update.effective_user.id
        if not await is_premium(user_id):
            await update.message.reply_markdown(
                "🔮 This is a **premium feature**.\n"
                "Upgrade with /buyweek or /buymonth to unlock."
            )
            return

        question = " ".join(context.args) if context.args else "General guidance"
        
        # Draw ten cards for Celtic Cross
        cards = await api.draw_tarot_cards(count=10)
        
        if not cards or len(cards) < 10:
            await update.message.reply_text("Unable to draw all cards. Please try again.")
            return
        
        positions = [
            "Present", "Challenge", "Past", "Future", "Above (Conscious)",
            "Below (Subconscious)", "Advice", "External", "Hopes/Fears", "Outcome"
        ]
        
        text = f"**🔮 Celtic Cross**\n*Question:* {question}\n\n"
        for i, card in enumerate(cards[:10]):
            card_name = card.get('name', 'Unknown')
            suit = card.get('suit', '')
            keywords = card.get('keywords', [])
            keywords_str = ', '.join(keywords[:2]) if keywords else ''
            
            text += f"**{positions[i]}:** {card_name}\n"
            if i < 5:  # Show more detail for first few positions
                text += f"_{keywords_str}_\n"
            text += "\n"
        
        text += "_Full interpretations available in the complete version._"
        
        await update.message.reply_markdown(text)
    except Exception as e:
        print(f"Error in celtic_cross: {e}")
        await update.message.reply_text("Unable to generate spread. Please try again.")
