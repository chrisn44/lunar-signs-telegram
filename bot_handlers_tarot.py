import random
from telegram import Update
from telegram.ext import ContextTypes
from bot_services_professional_api import get_api
from bot_utils_helpers import is_premium
import asyncio

api = get_api()

def format_card_name(card_data: dict) -> str:
    """Format card name nicely"""
    name = card_data.get('name', 'Unknown Card')
    return name

def get_card_suit_symbol(suit: str) -> str:
    """Get symbol for suit"""
    symbols = {
        'wands': '🔥',
        'cups': '💧',
        'swords': '⚔️',
        'pentacles': '💰',
        'major': '🌟'
    }
    return symbols.get(suit.lower() if suit else 'major', '🃏')

async def daily_tarot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Free: one random card with ONLY real data from API."""
    try:
        # Send typing action
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Draw one random card from Zodii API
        cards = await api.draw_tarot_cards(count=1)
        
        if not cards or len(cards) == 0:
            await update.message.reply_text("The cards are shuffling... please try again.")
            return
        
        card = cards[0]  # First card from the draw
        
        # Extract ONLY real data from API
        card_name = card.get('name', 'Unknown')
        suit = card.get('suit', '')
        rank = card.get('rank', '')
        keywords = card.get('keywords', [])
        description = card.get('description', '')  # Some APIs have description
        fortune_telling = card.get('fortune_telling', [])  # Some APIs have predictions
        
        # Format keywords
        keywords_str = ', '.join(keywords) if keywords else ''
        
        # Get symbol
        symbol = get_card_suit_symbol(suit)
        
        # Build title
        if suit and rank:
            title = f"{symbol} **{card_name}** ({rank} of {suit.title()})"
        else:
            title = f"{symbol} **{card_name}** (Major Arcana)"
        
        # Build message using ONLY real data
        text = f"🃏 **Your Tarot Card**\n\n{title}\n\n"
        
        if keywords_str:
            text += f"**Keywords:** {keywords_str}\n\n"
        
        # Add description if available
        if description:
            text += f"{description}\n\n"
        
        # Add fortune telling if available
        if fortune_telling and len(fortune_telling) > 0:
            text += f"**Fortune:** {random.choice(fortune_telling)}\n\n"
        
        text += "_⚡ Premium users get 3-card spreads with /spread_"
        
        await update.message.reply_markdown(text)
        
    except Exception as e:
        print(f"❌ Error in daily_tarot: {e}")
        await update.message.reply_text("The cards are not ready. Please try again later.")

async def three_card_spread(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Premium: past-present-future spread with ONLY real data."""
    try:
        user_id = update.effective_user.id
        if not await is_premium(user_id):
            await update.message.reply_markdown(
                "🔮 **Premium Feature**\n\n"
                "Three-card spreads are available for premium users.\n\n"
                "Upgrade with /buyweek (50⭐) or /buymonth (150⭐)"
            )
            return

        question = " ".join(context.args) if context.args else "General guidance"
        
        # Send typing action
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
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
            description = card.get('description', '')
            
            symbol = get_card_suit_symbol(suit)
            
            if suit and rank:
                card_display = f"{symbol} **{card_name}** ({rank} of {suit.title()})"
            else:
                card_display = f"{symbol} **{card_name}** (Major Arcana)"
            
            keywords_str = ', '.join(keywords[:2]) if keywords else ''
            
            text += f"**{positions[i]}:** {card_display}\n"
            if keywords_str:
                text += f"*Keywords:* {keywords_str}\n"
            if description:
                # Use first sentence only for brevity in spreads
                short_desc = description.split('.')[0] + '.'
                text += f"*{short_desc}*\n"
            text += "\n"
        
        await update.message.reply_markdown(text)
        
    except Exception as e:
        print(f"❌ Error in three_card_spread: {e}")
        await update.message.reply_text("Unable to generate spread. Please try again.")

async def celtic_cross(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Premium: full 10-card Celtic Cross."""
    try:
        user_id = update.effective_user.id
        if not await is_premium(user_id):
            await update.message.reply_markdown(
                "🔮 **Premium Feature**\n\n"
                "The Celtic Cross is available for premium users.\n\n"
                "Upgrade with /buyweek or /buymonth to unlock!"
            )
            return

        question = " ".join(context.args) if context.args else "General guidance"
        
        # Send typing action
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Draw ten cards
        cards = await api.draw_tarot_cards(count=10)
        
        if not cards or len(cards) < 10:
            await update.message.reply_text("Unable to draw all cards. Please try again.")
            return
        
        positions = [
            "Present", "Challenge", "Past", "Future", "Above",
            "Below", "Advice", "External", "Hopes/Fears", "Outcome"
        ]
        
        text = f"**🔮 Celtic Cross Spread**\n*Question:* {question}\n\n"
        
        for i in range(min(5, len(cards))):
            card = cards[i]
            card_name = card.get('name', 'Unknown')
            suit = card.get('suit', '')
            
            symbol = get_card_suit_symbol(suit)
            
            if suit and card.get('rank'):
                card_display = f"{symbol} **{card_name}** ({card.get('rank')} of {suit.title()})"
            else:
                card_display = f"{symbol} **{card_name}**"
            
            text += f"**{positions[i]}:** {card_display}\n"
        
        text += f"\n_✨ Full 10-card reading available in the complete version._"
        
        await update.message.reply_markdown(text)
        
    except Exception as e:
        print(f"❌ Error in celtic_cross: {e}")
        await update.message.reply_text("Unable to generate spread. Please try again.")
