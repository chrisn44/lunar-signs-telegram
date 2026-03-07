# LunarSignsBot 🌙

A Telegram bot that provides daily horoscopes and tarot readings. Free tier includes basic horoscopes and a daily tarot card. Premium unlocks detailed forecasts, unlimited tarot spreads, compatibility, and more – all purchased with Telegram Stars.

## Features

- **Horoscopes**: Daily, weekly, monthly (free basic; premium detailed)
- **Tarot**: Daily card (free), 3‑card spread, Celtic Cross (premium)
- **Premium**: Unlock with Telegram Stars (50⭐/week, 150⭐/month)
- **Anti‑spam**: Rate limiting + captcha for new users
- **Admin panel**: Broadcast messages, view stats

## Commands

| Command | Description | Access |
|--------|-------------|--------|
| `/start` | Set your zodiac sign | Free |
| `/horoscope` | Today's horoscope | Free |
| `/weekly` | Weekly overview | Free |
| `/tarot` | Daily tarot card | Free |
| `/spread` | 3‑card spread (past‑present‑future) | Premium |
| `/celtic` | Celtic Cross spread | Premium |
| `/premium` | Info about premium plans | Free |
| `/buy_week` | Purchase 1‑week premium (50⭐) | Free |
| `/buy_month` | Purchase 1‑month premium (150⭐) | Free |
| `/compatibility` | Check sign compatibility | Premium |
| `/admin` | Admin commands | Admins only |

## Premium Perks

- Unlimited daily horoscopes (detailed love, career, health)
- Extended monthly forecast (PDF)
- Unlimited tarot spreads with full interpretations
- Compatibility checker
- Priority support
- No ads

## Technologies Used

- Python 3.11
- python-telegram-bot v20.7
- PostgreSQL (SQLAlchemy async)
- Redis for rate limiting
- Docker for containerization
- Telegram Stars for payments

---

Enjoy the stars! ✨
