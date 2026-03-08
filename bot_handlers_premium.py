from telegram import Update, LabeledPrice
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from bot_database import get_db
from bot_utils_helpers import is_premium
from bot_config import ADMIN_IDS
import logging
import random
import traceback

# Premium prices in Telegram Stars - CORRECTED (no multiplication needed)
PREMIUM_WEEK_STARS = 50
PREMIUM_MONTH_STARS = 150

logger = logging.getLogger(__name__)

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show premium information."""
    try:
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
            "Use /buyweek or /buymonth to purchase."
        )
        await update.message.reply_markdown(text)
        logger.info(f"Premium info sent to user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error in info: {e}")
        await update.message.reply_text("Sorry, unable to show premium info.")

async def buy_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send invoice for 1-week premium."""
    logger.info(f"Buy week command received from user {update.effective_user.id}")
    await send_invoice(update, context, "1-Week Premium", "premium_week", PREMIUM_WEEK_STARS)

async def buy_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send invoice for 1-month premium."""
    logger.info(f"Buy month command received from user {update.effective_user.id}")
    await send_invoice(update, context, "1-Month Premium", "premium_month", PREMIUM_MONTH_STARS)

async def send_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE, title: str, payload: str, stars: int):
    """Helper to send a Telegram Stars invoice."""
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        logger.info(f"Preparing invoice for user {user_id}: {title} for {stars} stars")
        
        # Currency must be XTR for Telegram Stars
        currency = "XTR"
        # For Telegram Stars, use the exact star amount - NO MULTIPLICATION
        prices = [LabeledPrice(title, stars)]  # ← FIXED: removed * 100
        
        # Send the invoice using context.bot
        await context.bot.send_invoice(
            chat_id=chat_id,
            title=title,
            description=f"Unlock all premium features for {title.lower()}",
            payload=payload,
            provider_token="",  # Must be empty for Stars
            currency=currency,
            prices=prices,
            start_parameter="premium-access"
        )
        logger.info(f"Invoice sent successfully to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending invoice: {e}")
        logger.error(traceback.format_exc())
        await update.message.reply_text("Sorry, unable to process payment at this time. Please try again later.")

async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pre-checkout query (verify payload)."""
    query = update.pre_checkout_query
    logger.info(f"Pre-checkout query received: {query.invoice_payload} from user {query.from_user.id}")
    
    # Validate the payload
    if query.invoice_payload not in ["premium_week", "premium_month"]:
        logger.warning(f"Invalid payload: {query.invoice_payload}")
        await query.answer(ok=False, error_message="Invalid purchase. Please try again.")
        return
    
    # You can add additional checks here (e.g., user already premium?)
    await query.answer(ok=True)  # Confirm the payment
    logger.info(f"Pre-checkout approved for user {query.from_user.id}")

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle successful payment - grant premium access."""
    try:
        user_id = update.effective_user.id
        payment = update.message.successful_payment
        stars_spent = payment.total_amount  # ← FIXED: removed // 100
        payload = payment.invoice_payload
        payment_id = payment.provider_payment_charge_id  # Unique payment ID

        logger.info(f"✅ Successful payment from user {user_id}: {stars_spent} stars for {payload}")

        db = await get_db()
        user = db.get_user(user_id)

        if not user:
            # Should not happen, but create user if missing
            user = db.create_user(user_id, update.effective_user.username)

        now = datetime.now()
        if payload == "premium_week":
            expiry = now + timedelta(days=7)
            item = "week"
        elif payload == "premium_month":
            expiry = now + timedelta(days=30)
            item = "month"
        else:
            # Fallback (should not happen)
            expiry = now + timedelta(days=7)
            item = "unknown"

        # Update user premium status
        db.update_user(
            user_id,
            is_premium=True,
            premium_until=expiry.isoformat()
        )

        # Record payment
        db.add_payment(
            user_id=user_id,
            payment_id=payment_id,
            stars=stars_spent,
            item=item
        )

        # Confirm to user
        await update.message.reply_text(
            f"✅ **Thank you for your purchase!**\n\n"
            f"You now have premium access until **{expiry.strftime('%Y-%m-%d')}**.\n"
            f"Enjoy all the premium features! ✨",
            parse_mode='Markdown'
        )
        
        logger.info(f"Premium activated for user {user_id} until {expiry}")

    except Exception as e:
        logger.error(f"Error processing successful payment: {e}")
        logger.error(traceback.format_exc())
        await update.message.reply_text(
            "Thank you for your payment! There was a small issue activating your premium. "
            "Please contact support with your payment ID."
        )

# The rest of your file (compatibility, my_premium, grant_premium) remains the same
async def compatibility(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Premium feature: check compatibility between two signs."""
    try:
        user_id = update.effective_user.id
        if not await is_premium(user_id):
            await update.message.reply_markdown(
                "💞 Compatibility is a **premium feature**. Upgrade to see how signs match!\n"
                "Use /buyweek or /buymonth to get premium."
            )
            return

        args = context.args
        if len(args) < 2:
            await update.message.reply_text(
                "Usage: /compatibility <sign1> <sign2>\n"
                "Example: /compatibility aries libra"
            )
            return

        sign1, sign2 = args[0].lower(), args[1].lower()
        
        # Simple compatibility calculation based on element
        elements = {
            "aries": "fire", "leo": "fire", "sagittarius": "fire",
            "taurus": "earth", "virgo": "earth", "capricorn": "earth",
            "gemini": "air", "libra": "air", "aquarius": "air",
            "cancer": "water", "scorpio": "water", "pisces": "water"
        }
        
        el1 = elements.get(sign1, "unknown")
        el2 = elements.get(sign2, "unknown")
        
        # Compatibility by element
        if el1 == el2:
            base_score = 85
            comment = "You share the same element – great harmony and understanding!"
        elif (el1 == "fire" and el2 == "air") or (el1 == "air" and el2 == "fire"):
            base_score = 90
            comment = "Fire and air – passion meets intellect! A dynamic duo."
        elif (el1 == "earth" and el2 == "water") or (el1 == "water" and el2 == "earth"):
            base_score = 88
            comment = "Earth and water – nurturing and stable. A grounded connection."
        elif (el1 == "fire" and el2 == "earth") or (el1 == "earth" and el2 == "fire"):
            base_score = 65
            comment = "Fire and earth – can be challenging but growth comes from effort."
        elif (el1 == "air" and el2 == "water") or (el1 == "water" and el2 == "air"):
            base_score = 70
            comment = "Air and water – emotions meet thoughts. Requires communication."
        else:
            base_score = 75
            comment = "An interesting mix – with mutual respect, you can create magic."
        
        # Add a little randomness (±5) for variety
        score = base_score + random.randint(-5, 5)
        score = max(0, min(100, score))
        
        await update.message.reply_markdown(
            f"**💞 Compatibility: {sign1.title()} + {sign2.title()}**\n\n"
            f"Score: **{score}%**\n"
            f"{comment}\n\n"
            f"_For a detailed analysis, check back soon!_"
        )
    except Exception as e:
        logger.error(f"Error in compatibility: {e}")
        await update.message.reply_text("Sorry, unable to calculate compatibility at this time.")

async def my_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check your premium status."""
    try:
        user_id = update.effective_user.id
        
        # Check if admin
        if user_id in ADMIN_IDS:
            await update.message.reply_text(
                "👑 **Admin Premium Access**\n\n"
                "As an admin, you have automatic premium access to all features!",
                parse_mode='Markdown'
            )
            return
            
        if await is_premium(user_id):
            db = await get_db()
            user = db.get_user(user_id)
            expiry = user.get('premium_until')
            if expiry:
                from dateutil import parser
                if isinstance(expiry, str):
                    expiry_dt = parser.parse(expiry)
                else:
                    expiry_dt = expiry
                expiry_str = expiry_dt.strftime('%Y-%m-%d')
                await update.message.reply_text(
                    f"✅ You have premium access until **{expiry_str}**.",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text("✅ You have premium access (no expiry set).")
        else:
            await update.message.reply_text(
                "❌ You don't have premium. Use /buyweek or /buymonth to upgrade!"
            )
    except Exception as e:
        logger.error(f"Error in my_premium: {e}")
        await update.message.reply_text("Error checking premium status.")

async def grant_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to grant premium to a user."""
    user_id = update.effective_user.id
    
    # Check if user is admin
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ This command is for admins only.")
        return
    
    # Check if user ID provided
    if not context.args:
        await update.message.reply_text(
            "Usage: /grant <user_id> [week/month]\n"
            "Example: /grant 123456789 month"
        )
        return
    
    try:
        target_user_id = int(context.args[0])
        duration = context.args[1].lower() if len(context.args) > 1 else "month"
        
        db = await get_db()
        user = db.get_user(target_user_id)
        
        if not user:
            # Create user if doesn't exist
            user = db.create_user(target_user_id)
            logger.info(f"Created new user {target_user_id}")
        
        now = datetime.now()
        if duration == "week":
            expiry = now + timedelta(days=7)
            item = "week"
        else:
            expiry = now + timedelta(days=30)
            item = "month"
        
        # Update user premium status
        db.update_user(
            target_user_id,
            is_premium=True,
            premium_until=expiry.isoformat()
        )
        
        await update.message.reply_text(
            f"✅ **Premium Granted!**\n\n"
            f"User: `{target_user_id}`\n"
            f"Duration: {item}\n"
            f"Expires: {expiry.strftime('%Y-%m-%d')}",
            parse_mode='Markdown'
        )
        
        logger.info(f"Admin {user_id} granted premium {item} to user {target_user_id}")
        
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID. Please provide a numeric ID.")
    except Exception as e:
        logger.error(f"Error granting premium: {e}")
        await update.message.reply_text(f"Error: {str(e)}")
