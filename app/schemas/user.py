from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    daily_card_limit: int
    target_retention: float
    streak: int
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserPreferences(BaseModel):
    daily_card_limit: Optional[int] = None
    target_retention: Optional[float] = None
    new_cards_per_day: Optional[int] = None