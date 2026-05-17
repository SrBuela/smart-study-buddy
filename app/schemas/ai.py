from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Union


class FlashcardItem(BaseModel):
    front: str
    back: str
    hint: Optional[str] = None
    topic: Optional[str] = None


class FlashcardGenerationRequest(BaseModel):
    text: str = Field(..., min_length=10)
    card_count: int = Field(default=10, ge=1, le=50)
    include_hints: bool = True
    topic: Optional[str] = None


class FlashcardGenerationResponse(BaseModel):
    cards: List[FlashcardItem]
    tokens_used: int
    estimated_cost: float


class NoteSummaryRequest(BaseModel):
    text: str = Field(..., min_length=10)
    max_length: Optional[int] = 500


class KeyTerm(BaseModel):
    term: str
    definition: str


class NoteSummaryResponse(BaseModel):
    summary: str
    key_points: List[str] = []
    key_terms: List[KeyTerm] = []
    word_count: int = 0


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: Union[int, str]
    explanation: Optional[str] = None


class QuizGenerationRequest(BaseModel):
    deck_id: str
    question_count: int = Field(default=10, ge=1, le=50)
    difficulty: Optional[str] = "medium"


class QuizResponse(BaseModel):
    questions: List[QuizQuestion]
    deck_id: str
    generated_at: datetime