from fastapi import APIRouter, Depends, HTTPException, Request
from app.services.ai_service import AIService
from app.routes.auth import get_current_user
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/api/ai", tags=["AI Features"])
ai_service = AIService()

# ---- Request models ----
class FlashcardRequest(BaseModel):
    text: str = Field(..., min_length=10)
    card_count: int = Field(default=10, ge=1, le=50)
    include_hints: bool = True

class SummaryRequest(BaseModel):
    text: str = Field(..., min_length=10)
    max_length: Optional[int] = 500

class QuizRequest(BaseModel):
    deck_id: str
    question_count: int = Field(default=10, ge=1, le=50)
    difficulty: Optional[str] = "medium"

@router.post("/generate-cards")
async def generate_flashcards(req: FlashcardRequest, request: Request, current_user = Depends(get_current_user)):
    try:
        cards = await ai_service.generate_flashcards(
            text=req.text,
            count=req.card_count,
            include_hints=req.include_hints,
        )
        return {
            "cards": cards,
            "tokens_used": len(req.text.split()) // 100 * req.card_count,
            "estimated_cost": 0.001 * req.card_count,
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/summarize")
async def summarize_notes(req: SummaryRequest, request: Request, current_user = Depends(get_current_user)):
    try:
        result = await ai_service.summarize_notes(req.text, req.max_length)
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/generate-quiz")
async def generate_quiz(req: QuizRequest, request: Request, current_user=Depends(get_current_user)):
    try:
        # Fetch real cards from the database
        cards_col = request.app.state.db["cards"]
        cursor = cards_col.find({"deck": req.deck_id, "owner": current_user["_id"]})
        cards = []
        async for doc in cursor:
            cards.append({"front": doc["front"], "back": doc["back"]})

        # Use the AI service (mock or real depending on key)
        questions = await ai_service.generate_quiz(
            cards_content=cards,
            question_count=req.question_count,
            difficulty=req.difficulty or "medium",
        )
        return {
            "questions": questions,
            "deck_id": req.deck_id,
            "generated_at": str(__import__('datetime').datetime.utcnow()),
        }
    except Exception as e:
        raise HTTPException(500, str(e))