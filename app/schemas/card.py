from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.card import CardState


class CardCreate(BaseModel):
    deck_id: str
    front: str
    back: str
    hint: Optional[str] = None
    topic: Optional[str] = None
    subtopic: Optional[str] = None


class CardUpdate(BaseModel):
    front: Optional[str] = None
    back: Optional[str] = None
    hint: Optional[str] = None
    topic: Optional[str] = None
    subtopic: Optional[str] = None


class CardResponse(BaseModel):
    id: str = Field(alias="_id")
    deck_id: str
    front: str
    back: Optional[str] = None
    hint: Optional[str] = None
    topic: Optional[str] = None
    state: CardState
    difficulty: float
    stability: float
    retrievability: float
    reps: int
    lapses: int
    due_date: datetime
    generated_by_ai: bool
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class CardReviewRequest(BaseModel):
    card_id: str
    rating: int = Field(..., ge=1, le=4, description="1=Again, 2=Hard, 3=Good, 4=Easy")
    response_time: float = Field(..., ge=0, description="Time taken to answer in seconds")


class CardReviewResponse(BaseModel):
    card_id: str
    rating: int
    new_state: str
    next_review: datetime
    stability: float
    difficulty: float