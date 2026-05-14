from beanie import Document, Link
from pydantic import Field
from datetime import datetime
from enum import Enum
from typing import Optional, List


class CardState(str, Enum):
    NEW = "new"
    LEARNING = "learning"
    REVIEW = "review"
    RELEARNING = "relearning"


class Card(Document):
    deck: Link["Deck"]
    owner: Link["User"]

    # Card content
    front: str
    back: str
    hint: Optional[str] = None

    # Topic for weak-topic detection
    topic: Optional[str] = None
    subtopic: Optional[str] = None

    # FSRS fields
    state: CardState = CardState.NEW
    difficulty: float = 0.0  # D in DSR model
    stability: float = 0.0  # S in DSR model
    retrievability: float = 0.0  # R in DSR model

    # Review history
    reps: int = 0
    lapses: int = 0
    last_review: Optional[datetime] = None
    due_date: datetime = Field(default_factory=datetime.utcnow)

    # AI metadata
    generated_by_ai: bool = False
    source_text: Optional[str] = None
    embedding: Optional[List[float]] = None  # For semantic search

    # Difficulty tracking
    user_difficulty_rating: Optional[float] = None  # User's perceived difficulty
    average_response_time: Optional[float] = None  # In seconds

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "cards"
        indexes = [
            [("owner", 1), ("due_date", 1)],
            [("deck", 1), ("state", 1)],
            "topic"
        ]