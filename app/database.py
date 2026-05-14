from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.user import User
from app.models.deck import Deck
from app.models.card import Card
from app.models.review import ReviewLog


async def init_db():
    # Create Motor client
    client = AsyncIOMotorClient(settings.MONGODB_URL)

    # Initialize beanie with the database and document models
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[
            User,
            Deck,
            Card,
            ReviewLog
        ]
    )