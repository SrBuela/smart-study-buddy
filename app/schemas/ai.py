from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class FlashcardGenerationRequest(BaseModel):
    text: str
    deck_id: Optional[str] = None
    card_count: int = Field(default=10, ge=1, le=50)
    include_hints: bool = False

class FlashcardGenerationResponse(BaseModel):
    cards: List[dict]
    tokens_used: int
    estimated_cost: float

class PDFGenerationRequest(BaseModel):
    deck_name: str
    card_count: int = Field(default=20, ge=1, le=100)

class NoteSummaryRequest(BaseModel):
    text: str
    max_length: int = Field(default=500, ge=100, le=2000)

class NoteSummaryResponse(BaseModel):
    summary: str
    key_points: List[str]
    key_terms: List[str]

class WeakTopicDetection(BaseModel):
    topic: str
    card_count: int
    average_lapses: float
    average_rating: float
    mastery_level: float

class QuizGenerationRequest(BaseModel):
    deck_id: str
    question_count: int = Field(default=5, ge=1, le=20)
    difficulty: str = "medium"  # easy, medium, hard

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    explanation: str

class QuizResponse(BaseModel):
    questions: List[QuizQuestion]
    deck_id: str
    generated_at: datetime