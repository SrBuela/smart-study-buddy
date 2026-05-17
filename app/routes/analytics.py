from fastapi import APIRouter, Depends, Request
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/stats")
async def get_stats(request: Request, current_user = Depends(get_current_user)):
    total_cards = await request.app.state.db["cards"].count_documents({"owner": current_user["_id"]})
    return {
        "total_reviews": 0,
        "average_rating": 0,
        "average_response_time": 0,
        "daily_reviews": {},
        "rating_distribution": {1:0,2:0,3:0,4:0},
        "retention_trend": [],
        "total_cards": total_cards,
        "streak": current_user.get("streak", 0),
    }

@router.get("/retention")
async def get_retention():
    return {"retention_rate": 100.0}

@router.get("/weak-topics")
async def weak_topics():
    return []