from beanie import Document, Indexed
from pydantic import EmailStr, Field
from datetime import datetime
from typing import Optional, List


class User(Document):
    email: Indexed(EmailStr, unique=True)
    username: str
    hashed_password: str
    full_name: Optional[str] = None

    # Study preferences
    daily_card_limit: int = 20
    target_retention: float = 0.9  # FSRS target retention rate
    new_cards_per_day: int = 10

    # Streak tracking
    streak: int = 0
    last_study_date: Optional[datetime] = None
    longest_streak: int = 0

    # FSRS personalized parameters (17 parameters)
    fsrs_parameters: Optional[List[float]] = None

    # Statistics
    total_cards_created: int = 0
    total_reviews: int = 0
    total_study_time: int = 0  # in seconds

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        indexes = [
            "email",
            "username"
        ]