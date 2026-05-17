from beanie import Document
from datetime import datetime
from typing import Optional, List
from pydantic import Field

class Deck(Document):
    name: str
    description: Optional[str] = None
    owner: str                       # plain string

    card_count: int = 0
    new_count: int = 0
    learning_count: int = 0
    review_count: int = 0

    subject: Optional[str] = None
    tags: List[str] = []
    color: Optional[str] = None

    ai_generated: bool = False
    source_document: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "decks"
        indexes = ["owner", "name"]