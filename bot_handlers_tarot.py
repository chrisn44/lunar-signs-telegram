import random
from telegram import Update
from telegram.ext import ContextTypes
from bot_services_professional_api import get_api
from bot_utils_helpers import is_premium
import asyncio

api = get_api()

# Rich tarot interpretations for premium users
TAROT_INTERPRETATIONS = {
    "love": [
        "This card suggests honesty and openness in your relationships today.",
        "Romantic opportunities may arise unexpectedly. Trust your heart.",
        "Focus on emotional connection rather than physical attraction.",
        "A partner may need extra attention and understanding.",
        "Single? Someone from your past might reappear.",
        "Communication is key in matters of the heart today."
    ],
    "career": [
        "Professional opportunities require your attention and focus.",
        "Trust your instincts when making work-related decisions.",
        "Collaboration with colleagues will prove valuable.",
        "A creative approach to problems will yield results.",
        "Financial matters need careful consideration today.",
        "Leadership opportunities may present themselves."
    ],
    "spiritual": [
        "Take time for reflection and meditation today.",
        "Trust the journey, even when the path isn't clear.",
        "Your intuition is especially strong right now.",
        "Past experiences are preparing you for what's ahead.",
        "Embrace change as a catalyst for growth.",
        "Connect with your inner wisdom for guidance."
    ]
}

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
    """Free: one random card with real meaning."""
    try:
        # Send typing action
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Draw one random card from Zodii API
        cards = await api.draw_tarot_cards(count=1)
        
        if not cards or len(cards) == 0:
            await update.message.reply_text("The cards are shuffling... please try again.")
            return
        
        card = cards[0]  # First card from the draw
        
        # Extract card info
        card_name = card.get('name', 'Unknown')
        suit = card.get('suit', '')
        rank = card.get('rank', '')
        keywords = card.get('keywords', [])
        keywords_str = ', '.join(keywords) if keywords else 'mystery, wisdom'
        
        # Get symbol
        symbol = get_card_suit_symbol(suit)
        
        # Build the message
        if suit and rank:
            # Full card with suit and rank
            title = f"{symbol} **{card_name}** ({rank} of {suit.title()})"
        else:
            # Major Arcana or without suit/rank
            title = f"{symbol} **{card_name}**"
        
        # Add a random insight for context
        insight = random.choice(TAROT_INTERPRETATIONS['spiritual'])
        
        text = (
            f"🃏 **Your Real Tarot Card**\n\n"
            f"{title}\n\n"
            f"**Keywords:** {keywords_str}\n\n"
            f"*{insight}*\n\n"
            f"_⚡ Premium users get full 3-card spreads with /spread_"
        )
        
        await update.message.reply_markdown(text)
        
    except Exception as e:
        print(f"❌ Error in daily_tarot: {e}")
        await update.message.reply_text("The cards are not ready. Please try again later.")

async def three_card_spread(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Premium: past-present-future spread with real cards."""
    try:
        user_id = update.effective_user.id
        if not await is_premium(user_id):
            await update.message.reply_markdown(
                "🔮 **Premium Feature**\n\n"
                "Three-card spreads with full interpretations are available for premium users.\n\n"
                "Upgrade with /buyweek (50⭐) or /buymonth (150⭐) to unlock all tarot spreads!"
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
            keywords_str = ', '.join(keywords[:2]) if keywords else 'wisdom'
            
            symbol = get_card_suit_symbol(suit)
            
            if suit and rank:
                card_display = f"{symbol} **{card_name}** ({rank} of {suit.title()})"
            else:
                card_display = f"{symbol} **{card_name}**"
            
            # Position-specific insight
            if i == 0:  # Past
                insight = "This energy has shaped your journey so far."
            elif i == 1:  # Present
                insight = "This is where you stand right now."
            else:  # Future
                insight = "This is the energy approaching you."
            
            text += f"**{positions[i]}:** {card_display}\n"
            text += f"_{keywords_str}_ – {insight}\n\n"
        
        text += "_✨ For deeper interpretations, try the Celtic Cross spread with /celtic_"
        
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
                "The Celtic Cross is our most detailed spread, available exclusively for premium users.\n\n"
                "Upgrade with /buyweek or /buymonth to unlock!"
            )
            return

        question = " ".join(context.args) if context.args else "General guidance"
        
        # Send typing action
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Draw ten cards for Celtic Cross
        cards = await api.draw_tarot_cards(count=10)
        
        if not cards or len(cards) < 10:
            await update.message.reply_text("Unable to draw all cards. Please try again.")
            return
        
        positions = [
            "Present", "Challenge", "Past", "Future", "Above (Conscious)",
            "Below (Subconscious)", "Advice", "External", "Hopes/Fears", "Outcome"
        ]
        
        text = f"**🔮 Celtic Cross Spread**\n*Question:* {question}\n\n"
        
        # Show first 5 cards in detail
        for i in range(5):
            card = cards[i]
            card_name = card.get('name', 'Unknown')
            suit = card.get('suit', '')
            rank = card.get('rank', '')
            keywords = card.get('keywords', [])
            keywords_str = ', '.join(keywords[:2]) if keywords else ''
            
            symbol = get_card_suit_symbol(suit)
            
            if suit and rank:
                card_display = f"{symbol} **{card_name}** ({rank} of {suit.title()})"
            else:
                card_display = f"{symbol} **{card_name}**"
            
            text += f"**{positions[i]}:** {card_display}\n"
            if keywords_str:
                text += f"_{keywordsstr}_\n"
            text += "\n"
        
        text += "_✨ The remaining 5 cards are revealed in the full version._"
        
        await update.message.reply_markdown(text)
        
    except Exception as e:
        print(f"❌ Error in celtic_cross: {e}")
        await update.message.reply_text("Unable to generate spread. Please try again.")
