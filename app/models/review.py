from beanie import Document, Link
from pydantic import Field
from datetime import datetime
from typing import Optional


class ReviewLog(Document):
    card: Link["Card"]
    user: Link["User"]
    deck: Link["Deck"]
    rating: int
    response_time: float
    scheduled_days: float
    state_before: str
    state_after: str
    stability_before: float
    stability_after: float
    difficulty_before: float
    difficulty_after: float
    session_id: Optional[str] = None
    review_date: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "reviews"