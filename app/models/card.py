from beanie import Document
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
    deck: str
    owner: str
    front: str
    back: str
    hint: Optional[str] = None
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    state: CardState = CardState.NEW
    difficulty: float = 0.0
    stability: float = 0.0
    retrievability: float = 0.0
    reps: int = 0
    lapses: int = 0
    last_review: Optional[datetime] = None
    due_date: datetime = Field(default_factory=datetime.utcnow)
    generated_by_ai: bool = False
    source_text: Optional[str] = None
    embedding: Optional[List[float]] = None
    user_difficulty_rating: Optional[float] = None
    average_response_time: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "cards"