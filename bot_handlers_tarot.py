import json
import random
from telegram import Update
from telegram.ext import ContextTypes
from bot_database import get_db
from bot_utils_helpers import is_premium

class TarotReader:
    def __init__(self):
        with open("tarot_cards.json", "r", encoding="utf-8") as f:
            self.cards = json.load(f)

    def draw_card(self, position_hint: str = None) -> dict:
        """Draw a random card, possibly reversed."""
        card = random.choice(self.cards)
        reversed = random.random() < 0.3  # 30% chance of reversal
        meaning = card["reversed"] if reversed else card["upright"]
        return {
            "name": card["name"],
            "meaning": meaning,
            "reversed": reversed,
            "keywords": card.get("keywords", []),
            "love": card.get("love", meaning),
            "career": card.get("career", meaning),
            "health": card.get("health", meaning)
        }

    def three_card_spread(self, question: str = "") -> dict:
        """Past, Present, Future with elemental analysis."""
        past = self.draw_card("past")
        present = self.draw_card("present")
        future = self.draw_card("future")

        elements = [c.get("element", "unknown") for c in [past, present, future]]
        return {
            "spread": "Three‑Card",
            "question": question,
            "cards": [
                {"position": "Past", **past},
                {"position": "Present", **present},
                {"position": "Future", **future}
            ],
            "analysis": f"Elements: {' - '.join(elements)}. "
                       f"Energy flows from {past['name']} through {present['name']} to {future['name']}."
        }

    def celtic_cross(self, question: str = "") -> dict:
        """Full 10‑card Celtic Cross with position meanings."""
        positions = [
            "Present", "Challenge", "Past", "Future", "Above (Conscious)",
            "Below (Subconscious)", "Advice", "External", "Hopes/Fears", "Outcome"
        ]
        cards = [self.draw_card(pos) for pos in positions]
        return {
            "spread": "Celtic Cross",
            "question": question,
            "cards": [{"position": positions[i], **cards[i]} for i in range(10)]
        }

# Initialize reader once
_reader = TarotReader()

async def daily_tarot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Free: one random card with brief meaning."""
    try:
        card = _reader.draw_card()
        await update.message.reply_markdown(
            f"🃏 **Your Daily Card: {card['name']}**\n"
            f"{'↕️ Reversed' if card['reversed'] else '⬆️ Upright'}\n\n"
            f"{card['meaning']}\n\n"
            f"❤️ Love: {card['love']}\n"
            f"💼 Career: {card['career']}\n"
            f"🏥 Health: {card['health']}"
        )
    except Exception as e:
        print(f"Error in daily_tarot: {e}")
        await update.message.reply_text("The cards are shuffling... please try again.")

async def three_card_spread(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Premium: past-present-future spread with analysis."""
    try:
        user_id = update.effective_user.id
        if not await is_premium(user_id):
            await update.message.reply_markdown(
                "🔮 This is a **premium feature**.\n"
                "Upgrade with /buyweek (50⭐) or /buymonth (150⭐) to unlock all tarot spreads."
            )
            return

        question = " ".join(context.args) if context.args else "General guidance"
        spread = _reader.three_card_spread(question)

        msg = f"**🔮 Three‑Card Spread**\n*Question:* {spread['question']}\n\n"
        for card in spread['cards']:
            msg += f"**{card['position']}:** {card['name']}\n"
            msg += f"_{card['meaning']}_\n\n"
        msg += f"**Analysis:** {spread['analysis']}"

        await update.message.reply_markdown(msg)
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
        spread = _reader.celtic_cross(question)

        msg = f"**🔮 Celtic Cross**\n*Question:* {spread['question']}\n\n"
        for card in spread['cards']:
            msg += f"**{card['position']}:** {card['name']}\n"
            msg += f"_{card['meaning']}_\n\n"

        await update.message.reply_markdown(msg)
    except Exception as e:
        print(f"Error in celtic_cross: {e}")
        await update.message.reply_text("Unable to generate spread. Please try again.")
