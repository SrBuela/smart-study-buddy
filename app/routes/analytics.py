from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict
from app.models.user import User
from app.services.analytics_service import AnalyticsService
from app.services.fsrs_service import FSRSService
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/ai", tags=["AI Features"])
analytics_service = AnalyticsService()
fsrs_service = FSRSService()


@router.get("/stats")
async def get_stats(
        days: int = Query(default=30, le=365),
        current_user: User = Depends(get_current_user)
):
    return await analytics_service.get_study_stats(
        user=current_user,
        days=days
    )


@router.get("/weak-topics")
async def get_weak_topics(current_user: User = Depends(get_current_user)):
    return await analytics_service.detect_weak_topics(user=current_user)


@router.get("/forecast")
async def get_forecast(
        days: int = Query(default=30, le=90),
        current_user: User = Depends(get_current_user)
):
    return await analytics_service.get_review_forecast(
        user=current_user,
        days=days
    )


@router.get("/retention")
async def get_retention(
        days: int = Query(default=30, le=365),
        current_user: User = Depends(get_current_user)
):
    retention_rate = await fsrs_service.get_retention_rate(
        user=current_user,
        days=days
    )
    return {"retention_rate": round(retention_rate * 100, 1)}


@router.get("/predict-retention/{card_id}")
async def predict_card_retention(
        card_id: str,
        days: int = Query(default=7, le=365),
        current_user: User = Depends(get_current_user)
):
    from app.models.card import Card

    card = await Card.get(card_id)
    if not card or str(card.owner.id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Card not found")

    prediction = await fsrs_service.predict_retention(card, days)
    return {
        "card_id": card_id,
        "days_from_now": days,
        "predicted_retention": round(prediction * 100, 1)
    }