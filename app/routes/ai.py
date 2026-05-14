from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.models.user import User
from app.schemas.ai import (
    FlashcardGenerationRequest, FlashcardGenerationResponse,
    NoteSummaryRequest, NoteSummaryResponse,
    QuizGenerationRequest, QuizResponse
)
from app.services.ai_service import AIService
from app.routes.auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/api/ai", tags=["AI Features"])
ai_service = AIService()

@router.post("/generate-cards", response_model=FlashcardGenerationResponse)
async def generate_flashcards(request: FlashcardGenerationRequest, current_user: User = Depends(get_current_user)):
    try:
        cards = await ai_service.generate_flashcards(
            text=request.text,
            count=request.card_count,
            include_hints=request.include_hints
        )
        return FlashcardGenerationResponse(
            cards=cards,
            tokens_used=len(request.text.split()) // 100 * request.card_count,
            estimated_cost=0.001 * request.card_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-from-pdf", response_model=FlashcardGenerationResponse)
async def generate_from_pdf(
    file: UploadFile = File(...),
    card_count: int = 20,
    current_user: User = Depends(get_current_user)
):
    try:
        import PyPDF2, io
        content = await file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text extracted from PDF")
        cards = await ai_service.generate_flashcards(text=text, count=card_count)
        return FlashcardGenerationResponse(
            cards=cards,
            tokens_used=len(text.split()) // 100 * card_count,
            estimated_cost=0.001 * card_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize", response_model=NoteSummaryResponse)
async def summarize_notes(request: NoteSummaryRequest, current_user: User = Depends(get_current_user)):
    try:
        result = await ai_service.summarize_notes(text=request.text, max_length=request.max_length)
        return NoteSummaryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizGenerationRequest, current_user: User = Depends(get_current_user)):
    try:
        from app.models.card import Card
        cards = await Card.find({"deck.id": request.deck_id}).to_list()
        if not cards:
            raise HTTPException(status_code=404, detail="No cards found in deck")
        cards_content = [{"front": card.front, "back": card.back} for card in cards]
        questions = await ai_service.generate_quiz(
            cards_content=cards_content,
            question_count=request.question_count,
            difficulty=request.difficulty
        )
        return QuizResponse(
            questions=questions,
            deck_id=request.deck_id,
            generated_at=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))