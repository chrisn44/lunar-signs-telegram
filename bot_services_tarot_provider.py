import json
import random

with open("tarot_cards.json", "r", encoding="utf-8") as f:
    TAROT_CARDS = json.load(f)

def get_random_card():
    return random.choice(TAROT_CARDS)

def get_spread(count: int):
    return random.sample(TAROT_CARDS, count)