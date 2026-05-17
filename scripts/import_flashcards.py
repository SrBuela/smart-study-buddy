import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add backend to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user import User
from app.models.deck import Deck
from app.models.card import Card
from app.core.config import settings


async def import_flashcards():
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    await init_beanie(database=db, document_models=[User, Deck, Card])
    print("Connected.")

    # Create demo user
    user = await User.find_one({"email": "demo@smartstudy.com"})
    if not user:
        user = User(
            email="demo@smartstudy.com",
            username="demo_user",
            hashed_password="$2b$12$KIXx4S.V7rK7y7FZt5L0ZOm9Xc2YIX8BZqq2n.XJG3NSZzH8Bb2Ki",
            full_name="Demo User"
        )
        await user.insert()
        print(f"Created user: {user.email}")
    else:
        print(f"User already exists: {user.email}")

    # Create deck
    deck = await Deck.find_one({"name": "Python W3Schools", "owner.id": str(user.id)})
    if not deck:
        deck = Deck(
            name="Python W3Schools",
            description="Complete Python flashcards from W3Schools",
            owner=user,
            subject="Programming",
            tags=["python", "w3schools", "beginner"],
            color="blue"
        )
        await deck.insert()
        print(f"Created deck: {deck.name}")
    else:
        print(f"Deck already exists: {deck.name}")

    # Load flashcards
    json_path = Path(__file__).parent.parent / 'data' / 'python_flashcards.json'
    if not json_path.exists():
        print(f"ERROR: File not found: {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        flashcards = json.load(f)

    # Import cards (avoid duplicates)
    imported = 0
    for card_data in flashcards:
        existing = await Card.find_one({
            "front": card_data["front"],
            "deck.id": str(deck.id)
        })
        if not existing:
            card = Card(
                deck=deck,
                owner=user,
                front=card_data["front"],
                back=card_data["back"],
                hint=card_data.get("hint", ""),
                topic=card_data.get("topic", ""),
                subtopic=card_data.get("subtopic", ""),
                due_date=datetime.now(timezone.utc)
            )
            await card.insert()
            imported += 1

    # Update deck counts
    total = await Card.find({"deck.id": str(deck.id)}).count()
    deck.card_count = total
    deck.new_count = total
    await deck.save()

    print(f"✅ Imported {imported} new flashcards.")
    print(f"Total cards in deck: {total}")

if __name__ == "__main__":
    asyncio.run(import_flashcards())