import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from functools import wraps
from bot_database import get_db
from bot_models import User
from bot_utils_helpers import get_user

captcha_store = {}

def generate_captcha():
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    op = random.choice(['+', '-'])
    if op == '+':
        answer = a + b
    else:
        a, b = max(a, b), min(a, b)
        answer = a - b
    question = f"What is {a} {op} {b}?"
    return question, str(answer)

def captcha_required(handler_func):
    @wraps(handler_func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        db_gen = get_db()
        db = await db_gen.__anext__()
        user = await get_user(db, user_id)
        if user and user.captcha_passed:
            await db_gen.aclose()
            return await handler_func(update, context, *args, **kwargs)

        if user_id in captcha_store:
            await update.message.reply_text("Please solve the captcha first:\n" + captcha_store[user_id]['question'])
            await db_gen.aclose()
            return

        question, answer = generate_captcha()
        captcha_store[user_id] = {'question': question, 'answer': answer, 'attempts': 0}
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
            "To prevent spam, solve this captcha:\n" + question,
            reply_markup=reply_markup
        )
        await db_gen.aclose()
    return wrapper

async def handle_captcha_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    data = query.data
    if data.startswith("captcha_"):
        answer = data.split("_")[1]
        if user_id not in captcha_store:
            await query.edit_message_text("Captcha expired. Please try again.")
            return
        if answer == captcha_store[user_id]['answer']:
            db_gen = get_db()
            db = await db_gen.__anext__()
            user = await get_user(db, user_id)
            user.captcha_passed = True
            await db.commit()
            await db_gen.aclose()
            del captcha_store[user_id]
            await query.edit_message_text("✅ Captcha passed! You can now use the bot.")
        else:
            captcha_store[user_id]['attempts'] += 1
            if captcha_store[user_id]['attempts'] >= 3:
                del captcha_store[user_id]
                await query.edit_message_text("Too many failed attempts. Start over with /start.")
            else:
                await query.edit_message_text(
                    f"❌ Wrong. Try again:\n{captcha_store[user_id]['question']}",
                    reply_markup=query.message.reply_markup
                )