from telegram import Update, LabeledPrice
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from bot_database import get_db
from bot_utils_helpers import is_premium

# Premium prices in Telegram Stars
PREMIUM_WEEK_STARS = 50
PREMIUM_MONTH_STARS = 150

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🌟 **LunarSignsBot Premium**\n\n"
        "Unlock the full cosmic experience:\n"
        "• Detailed daily horoscopes (love, career, health)\n"
        "• Extended monthly forecast\n"
        "• Unlimited tarot spreads (3‑card, Celtic Cross)\n"
        "• Compatibility checker\n"
        "• Priority support & no ads\n\n"
        f"**Prices**\n"
        f"• 1 week: {PREMIUM_WEEK_STARS} ⭐\n"
        f"• 1 month: {PREMIUM_MONTH_STARS} ⭐\n\n"
        "Use /buy_week or /buy_month to purchase."
    )
    await update.message.reply_markdown(text)

async def buy_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_invoice(update, "1-Week Premium", "premium_week", PREMIUM_WEEK_STARS)

async def buy_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_invoice(update, "1-Month Premium", "premium_month", PREMIUM_MONTH_STARS)

async def send_invoice(update: Update, title: str, payload: str, stars: int):
    try:
        chat_id = update.effective_chat.id
        description = f"Unlock all premium features for {title.lower()}"
        currency = "XTR"
        prices = [LabeledPrice(title, stars * 100)]
        
        await update.message.reply_invoice(
            title=title,
            description=description,
            payload=payload,
            provider_token="",
            currency=currency,
            prices=prices,
            start_parameter="premium-access"
        )
    except Exception as e:
        print(f"Error sending invoice: {e}")
        await update.message.reply_text("Sorry, unable to process payment at this time.")

async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    if query.invoice_payload not in ["premium_week", "premium_month"]:
        await query.answer(ok=False, error_message="Invalid purchase")
        return
    await query.answer(ok=True)

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        payment = update.message.successful_payment
        stars_spent = payment.total_amount // 100
        payload = payment.invoice_payload

        db = await get_db()
        user = db.get_user(user_id)

        now = datetime.now()
        if payload == "premium_week":
            expiry = now + timedelta(days=7)
            item = "week"
        else:
            expiry = now + timedelta(days=30)
            item = "month"

        # Update user premium status
        db.update_user(
            user_id, 
            is_premium=True, 
            premium_until=expiry.isoformat()
        )

        # Record payment
        db.add_payment(
            user_id=user_id,
            payment_id=payment.provider_payment_charge_id,
            stars=stars_spent,
            item=item
        )

        await update.message.reply_text(
            f"✅ Thank you! You now have premium access until {expiry.strftime('%Y-%m-%d')}."
        )
    except Exception as e:
        print(f"Error processing payment: {e}")
        await update.message.reply_text("Thank you for your purchase! Your premium access will be activated shortly.")

async def compatibility(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if not await is_premium(user_id):
            await update.message.reply_markdown(
                "💞 Compatibility is a **premium feature**. Upgrade to see how signs match!"
            )
            return

        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Usage: /compatibility <sign1> <sign2>\nExample: /compatibility aries libra")
            return

        sign1, sign2 = args[0].lower(), args[1].lower()
        
        # Simple compatibility calculation
        compatibility_scores = {
            ("aries", "leo"): 95, ("aries", "sagittarius"): 90, ("aries", "gemini"): 85,
            ("taurus", "virgo"): 95, ("taurus", "capricorn"): 90, ("taurus", "cancer"): 85,
            ("gemini", "libra"): 95, ("gemini", "aquarius"): 90, ("gemini", "aries"): 85,
            ("cancer", "scorpio"): 95, ("cancer", "pisces"): 90, ("cancer", "taurus"): 85,
            ("leo", "sagittarius"): 95, ("leo", "aries"): 90, ("leo", "libra"): 85,
            ("virgo", "capricorn"): 95, ("virgo", "taurus"): 90, ("virgo", "scorpio"): 85,
            ("libra", "aquarius"): 95, ("libra", "gemini"): 90, ("libra", "leo"): 85,
            ("scorpio", "pisces"): 95, ("scorpio", "cancer"): 90, ("scorpio", "virgo"): 85,
            ("sagittarius", "aries"): 95, ("sagittarius", "leo"): 90, ("sagittarius", "aquarius"): 85,
            ("capricorn", "taurus"): 95, ("capricorn", "virgo"): 90, ("capricorn", "scorpio"): 85,
            ("aquarius", "gemini"): 95, ("aquarius", "libra"): 90, ("aquarius", "sagittarius"): 85,
            ("pisces", "cancer"): 95, ("pisces", "scorpio"): 90, ("pisces", "taurus"): 85,
        }
        
        # Default score
        score = compatibility_scores.get((sign1, sign2), 
                compatibility_scores.get((sign2, sign1), 75))
        
        if score > 85:
            comment = "🌟 An excellent match! You complement each other perfectly."
        elif score > 70:
            comment = "✨ Good potential! With effort, this can be a great match."
        else:
            comment = "🌙 Interesting dynamic. You'll need to work on understanding each other."
        
        await update.message.reply_markdown(
            f"**{sign1.title()} + {sign2.title()} Compatibility**\n\n"
            f"Score: **{score}%**\n"
            f"{comment}"
        )
    except Exception as e:
        print(f"Error in compatibility: {e}")
        await update.message.reply_text("Sorry, unable to calculate compatibility at this time.")
