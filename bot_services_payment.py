from bot_database import get_db
from bot_models import Payment
from sqlalchemy import select

async def verify_payment(user_id: int, payment_id: str) -> bool:
    db_gen = get_db()
    db = await db_gen.__anext__()
    result = await db.execute(
        select(Payment).where(Payment.telegram_payment_id == payment_id)
    )
    payment = result.scalar_one_or_none()
    await db_gen.aclose()
    return payment is not None