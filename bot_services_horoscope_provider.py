import random
import datetime
from typing import Dict

class HoroscopeGenerator:
    """Generates rich, varied horoscopes without external APIs."""

    # Planetary rulers
    RULERS = {
        "aries": "Mars", "taurus": "Venus", "gemini": "Mercury",
        "cancer": "Moon", "leo": "Sun", "virgo": "Mercury",
        "libra": "Venus", "scorpio": "Pluto", "sagittarius": "Jupiter",
        "capricorn": "Saturn", "aquarius": "Uranus", "pisces": "Neptune"
    }

    # Elements
    ELEMENTS = {
        "aries": "fire", "leo": "fire", "sagittarius": "fire",
        "taurus": "earth", "virgo": "earth", "capricorn": "earth",
        "gemini": "air", "libra": "air", "aquarius": "air",
        "cancer": "water", "scorpio": "water", "pisces": "water"
    }

    # Modalities
    MODALITIES = {
        "aries": "cardinal", "cancer": "cardinal", "libra": "cardinal", "capricorn": "cardinal",
        "taurus": "fixed", "leo": "fixed", "scorpio": "fixed", "aquarius": "fixed",
        "gemini": "mutable", "virgo": "mutable", "sagittarius": "mutable", "pisces": "mutable"
    }

    # Sentence templates
    LOVE_TEMPLATES = [
        "Your ruling planet {ruler} aligns favorably with Venus, bringing warmth to your relationships.",
        "Single? A {adjective} encounter could happen {when}. Coupled? {advice}.",
        "Emotions run deep today. {advice} to strengthen your bonds.",
        "The {element} element in your sign makes you especially {trait} in matters of the heart.",
        "A {modality} energy pushes you to {action} in your love life."
    ]

    CAREER_TEMPLATES = [
        "Professional opportunities arise when {ruler} aspects Jupiter. {advice}",
        "Your {element} nature helps you {action} at work. Colleagues notice your {trait}.",
        "A {modality} approach is needed to {action} that project.",
        "Mercury's position favors {action} and networking. {advice}",
        "Financial prospects look {adjective} as {ruler} stabilizes."
    ]

    HEALTH_TEMPLATES = [
        "Your vitality is {adjective} today. Focus on {body_part}.",
        "The {element} element suggests you need {health_advice}.",
        "Energy levels are {energy} – {action} to maintain balance.",
        "A {modality} routine will help you {action} your well-being.",
        "{ruler} influences your {body_part}. Consider {health_advice}."
    ]

    # Word pools
    ADJECTIVES = ["exciting", "unexpected", "harmonious", "challenging", "inspiring", "transformative", "gentle", "powerful"]
    TRAITS = ["charming", "determined", "creative", "analytical", "intuitive", "practical", "adventurous", "loyal"]
    ACTIONS = ["take the lead", "collaborate", "reflect", "communicate", "plan ahead", "trust your instincts", "step back", "seize opportunities"]
    ADVICE = ["Be open to change.", "Stay grounded.", "Express your feelings.", "Double-check details.", "Follow your intuition.", "Take calculated risks.", "Nurture your connections."]
    BODY_PARTS = ["throat", "heart", "digestive system", "nervous system", "joints", "skin", "immune system"]
    ENERGY_LEVELS = ["high", "moderate", "fluctuating", "grounded", "creative"]
    HEALTH_ADVICE = ["gentle exercise", "meditation", "hydrate well", "rest", "eat nourishing foods", "stretching"]
    TIMES = ["in the morning", "during midday", "in the afternoon", "this evening", "late tonight"]

    @classmethod
    def generate(cls, sign: str, detailed: bool = False) -> Dict:
        """Generate a complete horoscope for a sign."""
        sign = sign.lower()
        ruler = cls.RULERS.get(sign, "the cosmos")
        element = cls.ELEMENTS.get(sign, "air")
        modality = cls.MODALITIES.get(sign, "cardinal")

        # Seed randomness with date + sign to ensure daily variation but consistency
        seed = int(datetime.date.today().strftime("%Y%m%d")) + sum(ord(c) for c in sign)
        rng = random.Random(seed)

        def pick(pool):
            return rng.choice(pool)

        # Build sentences
        love = pick(cls.LOVE_TEMPLATES).format(
            ruler=ruler, element=element, modality=modality,
            adjective=pick(cls.ADJECTIVES), trait=pick(cls.TRAITS),
            action=pick(cls.ACTIONS), advice=pick(cls.ADVICE), when=pick(cls.TIMES)
        )
        career = pick(cls.CAREER_TEMPLATES).format(
            ruler=ruler, element=element, modality=modality,
            adjective=pick(cls.ADJECTIVES), trait=pick(cls.TRAITS),
            action=pick(cls.ACTIONS), advice=pick(cls.ADVICE)
        )
        health = pick(cls.HEALTH_TEMPLATES).format(
            ruler=ruler, element=element, modality=modality,
            adjective=pick(cls.ADJECTIVES), energy=pick(cls.ENERGY_LEVELS),
            body_part=pick(cls.BODY_PARTS), health_advice=pick(cls.HEALTH_ADVICE),
            action=pick(cls.ACTIONS)
        )

        # Combine into overview
        overview = f"{love} {career} {health}"

        # Lucky numbers, color, mood
        lucky_numbers = [rng.randint(1, 9) for _ in range(3)]
        colors = ["Red", "Blue", "Green", "Yellow", "Purple", "Orange", "Silver", "Gold"]
        moods = ["Energetic", "Reflective", "Optimistic", "Calm", "Passionate", "Curious"]

        return {
            "overview": overview,
            "love": love,
            "career": career,
            "health": health,
            "lucky_numbers": lucky_numbers,
            "lucky_color": pick(colors),
            "mood": pick(moods),
            "source": "LunarSigns Astrology Engine"
        }

# Public async functions (to match existing bot structure)
async def get_today_horoscope(sign: str, detailed: bool = False) -> str:
    """Generate a rich horoscope for the given sign."""
    data = HoroscopeGenerator.generate(sign, detailed)
    if detailed:
        return (
            f"❤️ **Love:** {data['love']}\n\n"
            f"💼 **Career:** {data['career']}\n\n"
            f"🏥 **Health:** {data['health']}\n\n"
            f"🎨 **Color:** {data['lucky_color']}\n"
            f"🔢 **Lucky Numbers:** {', '.join(map(str, data['lucky_numbers']))}\n"
            f"😊 **Mood:** {data['mood']}"
        )
    else:
        return data['overview']

async def get_weekly_horoscope(sign: str, detailed: bool = False) -> str:
    """Generate a weekly forecast by combining daily variations."""
    if detailed:
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        forecast = f"**{sign.title()} – Weekly Premium Forecast**\n\n"
        for day in days[:5]:  # Show Mon-Fri in detail
            daily = HoroscopeGenerator.generate(sign, detailed=True)
            forecast += f"**{day}:** {daily['overview']}\n\n"
        forecast += f"**Weekend:** Focus on {HoroscopeGenerator.generate(sign, detailed=True)['love']}"
        return forecast
    else:
        # Brief weekly overview
        overview = HoroscopeGenerator.generate(sign, detailed=False)['overview'][:200]
        return f"**{sign.title()} – Weekly Overview**\n\n{overview}...\n\n_Upgrade to premium for daily breakdowns!_"
