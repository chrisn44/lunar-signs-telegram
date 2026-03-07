from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func
from bot_database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    sign = Column(Integer, nullable=True)          # 1-12 for zodiac
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_premium = Column(Boolean, default=False)
    premium_until = Column(DateTime(timezone=True), nullable=True)
    language = Column(String, default="en")
    captcha_passed = Column(Boolean, default=False)

class Payment(Base):
    __tablename__ = "payments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id"))
    telegram_payment_id = Column(String, unique=True)
    stars_amount = Column(Integer)
    purchased_item = Column(String)   # "week", "month"
    created_at = Column(DateTime(timezone=True), server_default=func.now())