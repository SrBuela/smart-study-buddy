from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/decks", tags=["Decks"])

class DeckCreate(BaseModel):
    name: str
    description: str = ""
    subject: str = ""
    tags: list = []

def _decks(request: Request):
    return request.app.state.db["decks"]

@router.post("/")
async def create_deck(data: DeckCreate, request: Request, current_user = Depends(get_current_user)):
    now = datetime.utcnow()
    doc = {
        "name": data.name,
        "description": data.description,
        "owner": current_user["_id"],
        "subject": data.subject,
        "tags": data.tags,
        "card_count": 0,
        "new_count": 0,
        "learning_count": 0,
        "review_count": 0,
        "created_at": now,
        "updated_at": now,
    }
    result = await _decks(request).insert_one(doc)
    return {"_id": str(result.inserted_id), "name": data.name, "card_count": 0}

@router.get("/")
async def list_decks(request: Request, current_user = Depends(get_current_user)):
    cursor = _decks(request).find({"owner": current_user["_id"]})
    decks = []
    async for d in cursor:
        d["_id"] = str(d["_id"])
        decks.append(d)
    return decks

@router.get("/{deck_id}")
async def get_deck(deck_id: str, request: Request, current_user = Depends(get_current_user)):
    d = await _decks(request).find_one({"_id": deck_id, "owner": current_user["_id"]})
    if not d:
        raise HTTPException(404, "Deck not found")
    d["_id"] = str(d["_id"])
    return d

@router.put("/{deck_id}")
async def update_deck(deck_id: str, data: DeckCreate, request: Request, current_user = Depends(get_current_user)):
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    result = await _decks(request).update_one(
        {"_id": deck_id, "owner": current_user["_id"]},
        {"$set": update_data}
    )
    if result.modified_count == 0:
        raise HTTPException(404, "Deck not found")
    return {"message": "updated"}

@router.delete("/{deck_id}")
async def delete_deck(deck_id: str, request: Request, current_user = Depends(get_current_user)):
    await _decks(request).delete_one({"_id": deck_id, "owner": current_user["_id"]})
    await request.app.state.db["cards"].delete_many({"deck": deck_id})
    return {"message": "deleted"}