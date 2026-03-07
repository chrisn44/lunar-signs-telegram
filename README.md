# LunarSignsBot 🌙

A Telegram bot that provides daily horoscopes and tarot readings. Free tier includes basic horoscopes and a daily tarot card. Premium unlocks detailed forecasts, unlimited tarot spreads, compatibility, and more – all purchased with Telegram Stars.

## Features

- **Horoscopes**: Daily, weekly, monthly (free basic; premium detailed)
- **Tarot**: Daily card (free), 3‑card spread, Celtic Cross (premium)
- **Premium**: Unlock with Telegram Stars (50⭐/week, 150⭐/month)
- **Anti‑spam**: Rate limiting + captcha for new users
- **Admin panel**: Broadcast messages, view stats

## Deployment

1. Create a bot with [@BotFather](https://t.me/BotFather) – name it **LunarSignsBot**.
2. Copy `.env.example` to `.env` and fill in your `BOT_TOKEN`.
3. Run locally: `docker-compose -f docker_compose.yml up --build`
4. Deploy on Railway: connect your GitHub repo and set the environment variables.

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

Enjoy the stars! ✨