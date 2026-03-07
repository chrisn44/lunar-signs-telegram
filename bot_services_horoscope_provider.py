import httpx
from bot_config import AZTRO_API_URL

async def get_today_horoscope(sign: str, detailed: bool = False) -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                AZTRO_API_URL,
                params={"sign": sign, "day": "today"}
            )
            if response.status_code == 200:
                data = response.json()
                if detailed:
                    # Build a rich premium horoscope
                    return (
                        f"❤️ **Love:** {data.get('love', 'N/A')}\n"
                        f"💼 **Career:** {data.get('career', 'N/A')}\n"
                        f"💰 **Wealth:** {data.get('wealth', 'N/A')}\n"
                        f"🏥 **Health:** {data.get('health', 'N/A')}\n"
                        f"🌈 **Color:** {data.get('color', 'N/A')}\n"
                        f"🔢 **Lucky Number:** {data.get('lucky_number', 'N/A')}"
                    )
                else:
                    return data.get("description", "No description available.")
        except:
            pass
    return "Unable to fetch horoscope at the moment."

async def get_weekly_horoscope(sign: str, detailed: bool = False) -> str:
    # For demo, return placeholder – in production use a real API
    if detailed:
        return f"Weekly forecast for {sign.title()} (detailed): ..."
    else:
        return f"Weekly overview for {sign.title()}: A week of growth and opportunities."