from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.deck import Deck
from app.models.user import User
from app.schemas.deck import DeckCreate, DeckUpdate, DeckResponse
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/ai", tags=["AI Features"])


@router.post("/", response_model=DeckResponse)
async def create_deck(
        deck_data: DeckCreate,
        current_user: User = Depends(get_current_user)
):
    deck = Deck(
        **deck_data.model_dump(),
        owner=current_user
    )
    await deck.insert()
    return deck


@router.get("/", response_model=List[DeckResponse])
async def get_decks(current_user: User = Depends(get_current_user)):
    decks = await Deck.find({"owner.id": str(current_user.id)}).to_list()
    return decks


@router.get("/{deck_id}", response_model=DeckResponse)
async def get_deck(
        deck_id: str,
        current_user: User = Depends(get_current_user)
):
    deck = await Deck.get(deck_id)
    if not deck or str(deck.owner.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Deck not found")
    return deck


@router.put("/{deck_id}", response_model=DeckResponse)
async def update_deck(
        deck_id: str,
        deck_data: DeckUpdate,
        current_user: User = Depends(get_current_user)
):
    deck = await Deck.get(deck_id)
    if not deck or str(deck.owner.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Deck not found")

    update_data = deck_data.model_dump(exclude_unset=True)
    await deck.set(update_data)

    return deck


@router.delete("/{deck_id}")
async def delete_deck(
        deck_id: str,
        current_user: User = Depends(get_current_user)
):
    deck = await Deck.get(deck_id)
    if not deck or str(deck.owner.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Deck not found")

    # Delete all cards in deck
    from app.models.card import Card
    await Card.find({"deck.id": deck_id}).delete()

    await deck.delete()
    return {"message": "Deck and all its cards deleted successfully"}