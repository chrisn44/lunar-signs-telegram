import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from functools import wraps
from bot_database import get_db

# Store captcha challenges in memory (exported for reset function)
captcha_store = {}

def generate_captcha():
    """Generate a simple math captcha."""
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    op = random.choice(['+', '-'])
    
    if op == '+':
        answer = a + b
        question = f"What is {a} + {b}?"
    else:
        # Ensure non-negative result
        a, b = max(a, b), min(a, b)
        answer = a - b
        question = f"What is {a} - {b}?"
    
    return question, str(answer)

def captcha_required(handler_func):
    """Decorator to require captcha for new users."""
    @wraps(handler_func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            user_id = update.effective_user.id
            
            # Get database
            db = await get_db()
            
            # Get user
            user = db.get_user(user_id)
            
            # If user doesn't exist, create them
            if not user:
                user = db.create_user(user_id, update.effective_user.username)
                print(f"Created new user {user_id}")
            
            # Debug: print user status
            print(f"User {user_id} captcha status: {user.get('captcha_passed')}")
            
            # Check if user already passed captcha
            if user and user.get('captcha_passed') == True:
                print(f"✅ User {user_id} already passed captcha - allowing access")
                return await handler_func(update, context, *args, **kwargs)
            
            # Check if there's an active captcha
            if user_id in captcha_store:
                # User needs to answer - prompt them again
                await update.message.reply_text(
                    f"🔐 Please solve the captcha first:\n{captcha_store[user_id]['question']}\n\n"
                    f"Click the buttons to enter your answer, then press Submit."
                )
                return
            
            # Generate new captcha
            question, answer = generate_captcha()
            captcha_store[user_id] = {
                'question': question,
                'answer': answer,
                'attempts': 0,
                'chat_id': update.effective_chat.id
            }
            
            print(f"Generated captcha for user {user_id}: {question} = {answer}")
            
            # Create keyboard with numbers 0-9
            keyboard = []
            
            # First row: 1,2,3
            row = []
            for i in range(1, 4):
                row.append(InlineKeyboardButton(str(i), callback_data=f"captcha_{i}"))
            keyboard.append(row)
            
            # Second row: 4,5,6
            row = []
            for i in range(4, 7):
                row.append(InlineKeyboardButton(str(i), callback_data=f"captcha_{i}"))
            keyboard.append(row)
            
            # Third row: 7,8,9
            row = []
            for i in range(7, 10):
                row.append(InlineKeyboardButton(str(i), callback_data=f"captcha_{i}"))
            keyboard.append(row)
            
            # Fourth row: 0
            keyboard.append([InlineKeyboardButton("0", callback_data="captcha_0")])
            
            # Fifth row: Submit (for multi-digit answers)
            keyboard.append([InlineKeyboardButton("✅ Submit Answer", callback_data="captcha_submit")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"🔐 To prevent spam, please solve this captcha:\n{question}\n\n"
                f"Click the buttons to enter your answer, then press Submit.",
                reply_markup=reply_markup
            )
            
            # Initialize user's input
            if 'captcha_input' not in context.user_data:
                context.user_data['captcha_input'] = {}
            context.user_data['captcha_input'][user_id] = ""
            
        except Exception as e:
            print(f"Error in captcha_required: {e}")
            import traceback
            traceback.print_exc()
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
        
        # Initialize input storage if needed
        if 'captcha_input' not in context.user_data:
            context.user_data['captcha_input'] = {}
        if user_id not in context.user_data['captcha_input']:
            context.user_data['captcha_input'][user_id] = ""
        
        if data.startswith("captcha_"):
            number = data.split("_")[1]
            
            if number == "submit":
                # User pressed submit - check their answer
                user_answer = context.user_data['captcha_input'].get(user_id, "")
                
                if user_id not in captcha_store:
                    await query.edit_message_text("❌ Captcha expired. Please try /start again.")
                    return
                
                correct_answer = captcha_store[user_id]['answer']
                
                print(f"User {user_id} submitted answer: '{user_answer}', correct: '{correct_answer}'")
                
                if user_answer == correct_answer:
                    # Captcha passed
                    print(f"✅ User {user_id} passed captcha - updating database")
                    db = await get_db()
                    db.update_user(user_id, captcha_passed=True)
                    
                    # Verify it was saved
                    user = db.get_user(user_id)
                    print(f"User after update: captcha_passed={user.get('captcha_passed')}")
                    
                    # Clean up
                    if user_id in captcha_store:
                        del captcha_store[user_id]
                    if user_id in context.user_data.get('captcha_input', {}):
                        context.user_data['captcha_input'].pop(user_id, None)
                    
                    await query.edit_message_text("✅ Captcha passed! You can now use the bot.")
                    
                else:
                    captcha_store[user_id]['attempts'] += 1
                    if captcha_store[user_id]['attempts'] >= 3:
                        # Too many attempts - clear captcha
                        if user_id in captcha_store:
                            del captcha_store[user_id]
                        if user_id in context.user_data.get('captcha_input', {}):
                            context.user_data['captcha_input'].pop(user_id, None)
                        await query.edit_message_text("❌ Too many failed attempts. Please start over with /start.")
                    else:
                        # Reset input and try again
                        context.user_data['captcha_input'][user_id] = ""
                        await query.edit_message_text(
                            f"❌ Wrong answer. Try again:\n{captcha_store[user_id]['question']}\n\n"
                            f"Click the buttons to enter your answer, then press Submit.",
                            reply_markup=query.message.reply_markup
                        )
            else:
                # User pressed a number button - add to their input
                current_input = context.user_data['captcha_input'].get(user_id, "")
                
                # Limit to reasonable length (answers won't be more than 3 digits)
                if len(current_input) < 3:
                    new_input = current_input + number
                    context.user_data['captcha_input'][user_id] = new_input
                    
                    # Show current input
                    display_text = f"Your answer: {new_input}\n\nContinue entering numbers, then press Submit."
                    
                    await query.edit_message_text(
                        display_text,
                        reply_markup=query.message.reply_markup
                    )
                else:
                    await query.answer("Maximum 3 digits allowed", show_alert=False)
    
    except Exception as e:
        print(f"Error in handle_captcha_answer: {e}")
        import traceback
        traceback.print_exc()
        try:
            await query.edit_message_text("❌ Error processing captcha. Please try /start again.")
        except:
            pass

async def reset_captcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset captcha for user if stuck."""
    try:
        user_id = update.effective_user.id
        print(f"Resetting captcha for user {user_id}")
        
        # Clear from memory store
        if user_id in captcha_store:
            del captcha_store[user_id]
            print(f"Removed user {user_id} from captcha_store")
        
        # Clear from user_data
        if 'captcha_input' in context.user_data and user_id in context.user_data['captcha_input']:
            context.user_data['captcha_input'].pop(user_id, None)
            print(f"Removed user {user_id} from captcha_input")
        
        # Also reset in database if needed (optional)
        db = await get_db()
        user = db.get_user(user_id)
        if user and user.get('captcha_passed') == False:
            # Keep as false, just reset the in-memory state
            pass
        
        await update.message.reply_text(
            "✅ Captcha has been reset.\n"
            "Please use /start to begin again."
        )
        
    except Exception as e:
        print(f"Error in reset_captcha: {e}")
        await update.message.reply_text("Error resetting captcha. Please try again.")
