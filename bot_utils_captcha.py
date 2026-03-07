import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from functools import wraps
from bot_database import get_db

# Store captcha challenges in memory
captcha_store = {}

def generate_captcha():
    """Generate a simple math captcha."""
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    op = random.choice(['+', '-'])
    
    if op == '+':
        answer = a + b
    else:
        # Ensure non-negative result
        a, b = max(a, b), min(a, b)
        answer = a - b
    
    question = f"What is {a} {op} {b}?"
    return question, str(answer)

def captcha_required(handler_func):
    """Decorator to require captcha for new users."""
    @wraps(handler_func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            user_id = update.effective_user.id
            
            # Get database - FIXED: removed __anext__()
            db = await get_db()
            
            # Get user
            user = db.get_user(user_id)
            
            # Check if user already passed captcha
            if user and user.get('captcha_passed'):
                return await handler_func(update, context, *args, **kwargs)
            
            # Check if there's an active captcha
            if user_id in captcha_store:
                # User needs to answer
                await update.message.reply_text(
                    "Please solve the captcha first:\n" + captcha_store[user_id]['question']
                )
                return
            
            # Generate new captcha
            question, answer = generate_captcha()
            captcha_store[user_id] = {
                'question': question,
                'answer': answer,
                'attempts': 0
            }
            
            # Create keyboard with numbers
            keyboard = []
            row = []
            for i in range(1, 10):
                row.append(InlineKeyboardButton(str(i), callback_data=f"captcha_{i}"))
                if len(row) == 3:
                    keyboard.append(row)
                    row = []
            if row:
                keyboard.append(row)
            keyboard.append([InlineKeyboardButton("0", callback_data="captcha_0")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "To prevent spam, please solve this captcha:\n" + question,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            print(f"Error in captcha_required: {e}")
            # If captcha fails, still allow the handler (fallback)
            return await handler_func(update, context, *args, **kwargs)
    
    return wrapper

async def handle_captcha_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle captcha button presses."""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        data = query.data
        
        if data.startswith("captcha_"):
            answer = data.split("_")[1]
            
            if user_id not in captcha_store:
                await query.edit_message_text("Captcha expired. Please try again with /start.")
                return
            
            correct_answer = captcha_store[user_id]['answer']
            
            if answer == correct_answer:
                # Captcha passed
                db = await get_db()
                db.update_user(user_id, captcha_passed=True)
                
                del captcha_store[user_id]
                await query.edit_message_text("✅ Captcha passed! You can now use the bot.")
            else:
                captcha_store[user_id]['attempts'] += 1
                if captcha_store[user_id]['attempts'] >= 3:
                    del captcha_store[user_id]
                    await query.edit_message_text("Too many failed attempts. Please start over with /start.")
                else:
                    # Keep the keyboard for another try
                    await query.edit_message_text(
                        f"❌ Wrong answer. Try again:\n{captcha_store[user_id]['question']}",
                        reply_markup=query.message.reply_markup
                    )
    except Exception as e:
        print(f"Error in handle_captcha_answer: {e}")
        await query.edit_message_text("Error processing captcha. Please try /start again.")
