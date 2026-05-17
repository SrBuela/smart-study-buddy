import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.card import Card, CardState
from app.models.user import User
from app.models.deck import Deck
from app.core.config import settings

async def main():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(database=client[settings.DATABASE_NAME],
                      document_models=[User, Deck, Card])

    # Get the user
    user = await User.find_one({"email": "api_test@example.com"})
    if not user:
        print("User not found. Please register first.")
        return

    # Create a deck if none exists
    deck = await Deck.find_one({"owner": str(user.id)})
    if not deck:
        deck = Deck(name="Test Deck", description="Test", owner=str(user.id))
        await deck.insert()
        print(f"Created deck {deck.id}")

    # Create a card with plain strings
    card = Card(
        deck=str(deck.id),
        owner=str(user.id),
        front="Test question?",
        back="Test answer",
        state=CardState.NEW,
        due_date=datetime.utcnow(),
        stability=0,
        difficulty=0,
        reps=0,
        lapses=0,
        retrievability=0
    )
    await card.insert()
    print(f"✅ Card created with ID: {card.id}")

asyncio.run(main())