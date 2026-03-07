from telegram import Update, LabeledPrice
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from bot_config import PREMIUM_WEEK_STARS, PREMIUM_MONTH_STARS
from bot_database import get_db
from bot_models import User, Payment
from bot_utils_helpers import get_user

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🌟 **LunarSignsBot Premium**\n\n"
        "Unlock the full cosmic experience:\n"
        "• Detailed daily horoscopes (love, career, health)\n"
        "• Extended monthly forecast (PDF)\n"
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

async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    if query.invoice_payload not in ["premium_week", "premium_month"]:
        await query.answer(ok=False, error_message="Invalid purchase")
        return
    await query.answer(ok=True)

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    payment = update.message.successful_payment
    stars_spent = payment.total_amount // 100
    payload = payment.invoice_payload

    db_gen = get_db()
    db = await db_gen.__anext__()
    user = await get_user(db, user_id)

    now = datetime.utcnow()
    if payload == "premium_week":
        expiry = now + timedelta(days=7)
        item = "week"
    else:
        expiry = now + timedelta(days=30)
        item = "month"

    user.is_premium = True
    user.premium_until = expiry

    payment_record = Payment(
        user_id=user_id,
        telegram_payment_id=payment.provider_payment_charge_id,
        stars_amount=stars_spent,
        purchased_item=item
    )
    db.add(payment_record)
    await db.commit()
    await db_gen.aclose()

    await update.message.reply_text(
        f"✅ Thank you! You now have premium access until {expiry.strftime('%Y-%m-%d')}."
    )

async def compatibility(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    # Dummy compatibility – in production, use an algorithm or API
    score = random.randint(60, 100)
    await update.message.reply_markdown(
        f"**{sign1.title()} + {sign2.title()} Compatibility**\n\n"
        f"Score: **{score}%**\n"
        f"{'A wonderful match!' if score > 80 else 'Good potential with effort.'}"
    )