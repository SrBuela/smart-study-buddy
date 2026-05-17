from datetime import datetime, timezone
from typing import List, Optional, Tuple
from beanie import PydanticObjectId
from fsrs import Scheduler as FSRS, Card as FSRSCard, Rating, State
from app.models.card import Card, CardState
from app.models.review import ReviewLog
from app.models.user import User


class FSRSService:
    def __init__(self, parameters: Optional[List[float]] = None):
        self.scheduler = FSRS(parameters=parameters) if parameters else FSRS()

    def _our_card_to_fsrs(self, card: Card) -> FSRSCard:
        return FSRSCard(
            due=card.due_date,
            stability=card.stability,
            difficulty=card.difficulty,
            reps=card.reps,
            lapses=card.lapses,
            state=State[card.state.value.upper()],
            last_review=card.last_review,
        )

    def _fsrs_card_to_our(self, fsrs_card: FSRSCard, our_card: Card) -> Card:
        our_card.stability = fsrs_card.stability
        our_card.difficulty = fsrs_card.difficulty
        our_card.due_date = fsrs_card.due
        our_card.reps = fsrs_card.reps
        our_card.lapses = fsrs_card.lapses
        our_card.state = CardState(fsrs_card.state.value.lower())
        our_card.last_review = datetime.now(timezone.utc)
        return our_card

    async def review_card(
            self,
            card: Card,
            rating: int,
            user: User,
            response_time: float = 0,
            session_id: Optional[str] = None,
    ) -> Tuple[Card, ReviewLog]:
        rating_map = {1: Rating.Again, 2: Rating.Hard, 3: Rating.Good, 4: Rating.Easy}
        fsrs_rating = rating_map[rating]

        fsrs_card = self._our_card_to_fsrs(card)

        state_before = card.state.value
        stability_before = card.stability
        difficulty_before = card.difficulty

        new_fsrs_card, _ = self.scheduler.review_card(fsrs_card, fsrs_rating)

        scheduled_days = 0
        if card.last_review:
            scheduled_days = (datetime.now(timezone.utc) - card.last_review).days

        card = self._fsrs_card_to_our(new_fsrs_card, card)
        card.average_response_time = (
                (card.average_response_time or 0) * 0.9 + response_time * 0.1
        )
        await card.save()

        review_log = ReviewLog(
            card=card,
            user=user,
            deck=card.deck,
            rating=rating,
            response_time=response_time,
            scheduled_days=scheduled_days,
            state_before=state_before,
            state_after=card.state.value,
            stability_before=stability_before,
            stability_after=card.stability,
            difficulty_before=difficulty_before,
            difficulty_after=card.difficulty,
            session_id=session_id,
        )
        await review_log.insert()

        return card, review_log

    async def get_due_cards(
            self,
            user: User,
            limit: int = 20,
            deck_id: Optional[str] = None,
    ) -> List[Card]:
        now = datetime.now(timezone.utc)

        # Fix: use $id for Beanie linked documents
        query = {
            "owner.$id": PydanticObjectId(user.id),
            "$or": [
                {"state": "new"},
                {"due_date": {"$lte": now}},
            ],
        }
        if deck_id:
            query["deck.$id"] = PydanticObjectId(deck_id)

        new_cards = await Card.find(
            {"owner.$id": PydanticObjectId(user.id), "state": "new"}
        ).limit(limit // 2).to_list()

        review_limit = limit - len(new_cards)
        review_cards = await Card.find(
            {
                "owner.$id": PydanticObjectId(user.id),
                "due_date": {"$lte": now}
            }
        ).sort("due_date").limit(review_limit).to_list()

        return new_cards + review_cards

    async def get_retention_rate(self, user: User, days: int = 30) -> float:
        from datetime import timedelta
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Fix: use $id for Beanie linked documents
        reviews = await ReviewLog.find({
            "user.$id": PydanticObjectId(user.id),
            "review_date": {"$gte": start_date},
        }).to_list()

        if not reviews:
            return 0.0
        correct = sum(1 for r in reviews if r.rating >= 3)
        return correct / len(reviews)

    async def predict_retention(self, card: Card, days_from_now: int) -> float:
        from datetime import timedelta
        if card.last_review:
            future_date = datetime.now(timezone.utc) + timedelta(days=days_from_now)
            elapsed = (future_date - card.last_review).total_seconds() / (24 * 3600)
        else:
            elapsed = days_from_now

        if card.stability > 0:
            return min(1.0, max(0.0, (1 + elapsed / (9 * card.stability)) ** -1))
        return 0.0