from beanie import Document, Link
from pydantic import Field
from datetime import datetime
from typing import Optional, List
from app.models.user import User


class Deck(Document):
    name: str
    description: Optional[str] = None
    owner: Link[User]

    # Deck stats
    card_count: int = 0
    new_count: int = 0
    learning_count: int = 0
    review_count: int = 0

    # Metadata
    subject: Optional[str] = None
    tags: List[str] = []
    color: Optional[str] = None

    # AI metadata
    ai_generated: bool = False
    source_document: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "decks"
        indexes = [
            "owner",
            "name"
        ]