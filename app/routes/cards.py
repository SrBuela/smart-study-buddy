from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/cards", tags=["Cards"])

class CardCreate(BaseModel):
    deck_id: str
    front: str
    back: str
    hint: str = ""
    topic: str = ""

class CardReview(BaseModel):
    card_id: str
    rating: int = Field(..., ge=1, le=4)
    response_time: float = 0.0

def _cards(request: Request):
    return request.app.state.db["cards"]

@router.post("/")
async def create_card(data: CardCreate, request: Request, current_user = Depends(get_current_user)):
    now = datetime.utcnow()
    doc = {
        "deck": data.deck_id,
        "owner": current_user["_id"],
        "front": data.front,
        "back": data.back,
        "hint": data.hint,
        "topic": data.topic,
        "state": "new",
        "difficulty": 0.0,
        "stability": 0.0,
        "retrievability": 0.0,
        "reps": 0,
        "lapses": 0,
        "last_review": None,
        "due_date": now,
        "created_at": now,
        "updated_at": now,
    }
    result = await _cards(request).insert_one(doc)
    # increment deck counts
    await request.app.state.db["decks"].update_one(
        {"_id": data.deck_id},
        {"$inc": {"card_count": 1, "new_count": 1}}
    )
    return {
        "_id": str(result.inserted_id),
        "deck_id": data.deck_id,
        "front": data.front,
        "state": "new",
        "due_date": str(now)
    }

@router.get("/due")
async def get_due_cards(request: Request, current_user = Depends(get_current_user)):
    now = datetime.utcnow()
    cursor = _cards(request).find({
        "owner": current_user["_id"],
        "$or": [{"state": "new"}, {"due_date": {"$lte": now}}]
    }).limit(20)
    cards = []
    async for c in cursor:
        c["_id"] = str(c["_id"])
        cards.append(c)
    return cards

@router.post("/review")
async def review_card(data: CardReview, request: Request, current_user = Depends(get_current_user)):
    try:
        now = datetime.utcnow()
        result = await _cards(request).update_one(
            {
                "_id": ObjectId(data.card_id),
                "owner": current_user["_id"]
            },
            {
                "$set": {
                    "state": "review",
                    "last_review": now,
                    "due_date": now + timedelta(days=1),   # simple interval
                },
                "$inc": {"reps": 1}
            }
        )
        if result.modified_count == 0:
            return {"error": "Card not found or not yours"}
        return {
            "card_id": data.card_id,
            "new_state": "review",
            "next_review": str(now + timedelta(days=1))
        }
    except Exception as e:
        return {"error": str(e)}