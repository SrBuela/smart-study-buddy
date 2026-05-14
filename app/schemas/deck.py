from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class DeckCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    subject: Optional[str] = None
    tags: List[str] = []
    color: Optional[str] = None


class DeckUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    subject: Optional[str] = None
    tags: Optional[List[str]] = None
    color: Optional[str] = None


class DeckResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    description: Optional[str] = None
    subject: Optional[str] = None
    tags: List[str]
    color: Optional[str] = None
    card_count: int
    new_count: int
    learning_count: int
    review_count: int
    ai_generated: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True