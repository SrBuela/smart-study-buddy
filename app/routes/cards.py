from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.models.card import Card
from app.models.deck import Deck
from app.models.user import User
from app.schemas.card import (
    CardCreate, CardUpdate, CardResponse,
    CardReviewRequest, CardReviewResponse
)
from app.services.fsrs_service import FSRSService
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/ai", tags=["AI Features"])
fsrs_service = FSRSService()


@router.post("/", response_model=CardResponse)
async def create_card(
        card_data: CardCreate,
        current_user: User = Depends(get_current_user)
):
    # Verify deck exists and belongs to user
    deck = await Deck.get(card_data.deck_id)
    if not deck or str(deck.owner.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Deck not found")

    card = Card(
        deck=deck,
        owner=current_user,
        front=card_data.front,
        back=card_data.back,
        hint=card_data.hint,
        topic=card_data.topic,
        subtopic=card_data.subtopic
    )
    await card.insert()

    # Update deck card count
    deck.card_count += 1
    deck.new_count += 1
    await deck.save()

    return card


@router.get("/due", response_model=List[CardResponse])
async def get_due_cards(
        deck_id: Optional[str] = None,
        limit: int = Query(default=20, le=50),
        current_user: User = Depends(get_current_user)
):
    cards = await fsrs_service.get_due_cards(
        user=current_user,
        limit=limit,
        deck_id=deck_id
    )
    return cards


@router.post("/review", response_model=CardReviewResponse)
async def review_card(
        review_data: CardReviewRequest,
        current_user: User = Depends(get_current_user)
):
    card = await Card.get(review_data.card_id)
    if not card or str(card.owner.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Card not found")

    updated_card, review_log = await fsrs_service.review_card(
        card=card,
        rating=review_data.rating,
        user=current_user,
        response_time=review_data.response_time
    )

    return CardReviewResponse(
        card_id=str(card.id),
        rating=review_data.rating,
        new_state=updated_card.state.value,
        next_review=updated_card.due_date,
        stability=updated_card.stability,
        difficulty=updated_card.difficulty
    )


@router.get("/{card_id}", response_model=CardResponse)
async def get_card(
        card_id: str,
        current_user: User = Depends(get_current_user)
):
    card = await Card.get(card_id)
    if not card or str(card.owner.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Card not found")
    return card


@router.put("/{card_id}", response_model=CardResponse)
async def update_card(
        card_id: str,
        card_data: CardUpdate,
        current_user: User = Depends(get_current_user)
):
    card = await Card.get(card_id)
    if not card or str(card.owner.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Card not found")

    update_data = card_data.model_dump(exclude_unset=True)
    await card.set(update_data)

    return card


@router.delete("/{card_id}")
async def delete_card(
        card_id: str,
        current_user: User = Depends(get_current_user)
):
    card = await Card.get(card_id)
    if not card or str(card.owner.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Card not found")

    # Update deck
    deck = await Deck.get(card.deck.id)
    if deck:
        deck.card_count -= 1
        if card.state == "new":
            deck.new_count -= 1
        await deck.save()

    await card.delete()
    return {"message": "Card deleted successfully"}