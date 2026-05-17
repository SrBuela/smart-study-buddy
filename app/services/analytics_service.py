from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone
from beanie import PydanticObjectId
from app.models.card import Card
from app.models.review import ReviewLog
from app.models.user import User
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:

    async def detect_weak_topics(
            self,
            user: User,
            min_lapses: int = 3,
            min_cards: int = 3
    ) -> List[Dict]:
        # Fix: use $id for Beanie linked documents
        weak_cards = await Card.find({
            "owner.$id": PydanticObjectId(user.id),
            "lapses": {"$gte": min_lapses}
        }).to_list()

        if len(weak_cards) < min_cards:
            return []

        topic_stats = {}
        for card in weak_cards:
            topic = card.topic or "Uncategorized"
            if topic not in topic_stats:
                topic_stats[topic] = {
                    "topic": topic,
                    "total_lapses": 0,
                    "total_ratings": 0,
                    "count": 0
                }
            topic_stats[topic]["total_lapses"] += card.lapses
            topic_stats[topic]["total_ratings"] += card.reps
            topic_stats[topic]["count"] += 1

        weak_topics = []
        for topic, stats in topic_stats.items():
            total = stats["total_lapses"] + stats["total_ratings"]
            if total == 0:
                continue
            avg_lapses = stats["total_lapses"] / stats["count"]
            mastery = 1 - (stats["total_lapses"] / total)

            if mastery < 0.7:
                weak_topics.append({
                    "topic": topic,
                    "card_count": stats["count"],
                    "average_lapses": round(avg_lapses, 2),
                    "mastery_level": round(mastery * 100, 1)
                })

        weak_topics.sort(key=lambda x: x["mastery_level"])
        return weak_topics[:5]

    async def get_study_stats(
            self,
            user: User,
            days: int = 30
    ) -> Dict:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Fix: use $id for Beanie linked documents
        reviews = await ReviewLog.find({
            "user.$id": PydanticObjectId(user.id),
            "review_date": {"$gte": start_date}
        }).to_list()

        if not reviews:
            return {
                "total_reviews": 0,
                "average_rating": 0,
                "average_response_time": 0,
                "daily_reviews": {},
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0},
                "retention_trend": [],
                "total_cards": await Card.find(
                    {"owner.$id": PydanticObjectId(user.id)}
                ).count(),
                "streak": user.streak,
                "longest_streak": user.longest_streak
            }

        total_reviews = len(reviews)
        avg_rating = sum(r.rating for r in reviews) / total_reviews
        avg_time = sum(r.response_time for r in reviews) / total_reviews

        daily_counts = {}
        for review in reviews:
            day = review.review_date.strftime("%Y-%m-%d")
            daily_counts[day] = daily_counts.get(day, 0) + 1

        rating_dist = {1: 0, 2: 0, 3: 0, 4: 0}
        for review in reviews:
            rating_dist[review.rating] += 1

        reviews_sorted = sorted(reviews, key=lambda r: r.review_date)
        retention_trend = []
        for i in range(0, len(reviews_sorted), 10):
            chunk = reviews_sorted[i:i + 10]
            retention = sum(1 for r in chunk if r.rating >= 3) / len(chunk)
            retention_trend.append({
                "date": chunk[-1].review_date.strftime("%Y-%m-%d"),
                "retention": round(retention * 100, 1)
            })

        return {
            "total_reviews": total_reviews,
            "average_rating": round(avg_rating, 2),
            "average_response_time": round(avg_time, 1),
            "daily_reviews": daily_counts,
            "rating_distribution": rating_dist,
            "retention_trend": retention_trend,
            "total_cards": await Card.find(
                {"owner.$id": PydanticObjectId(user.id)}
            ).count(),
            "streak": user.streak,
            "longest_streak": user.longest_streak
        }

    async def get_review_forecast(
            self,
            user: User,
            days: int = 30
    ) -> List[Dict]:
        forecast = []
        now = datetime.now(timezone.utc)

        for day in range(1, days + 1):
            date = now + timedelta(days=day)
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            # Fix: use $id for Beanie linked documents
            due_count = await Card.find({
                "owner.$id": PydanticObjectId(user.id),
                "due_date": {
                    "$gte": day_start,
                    "$lt": day_end
                }
            }).count()

            forecast.append({
                "date": date.strftime("%Y-%m-%d"),
                "due_count": due_count
            })

        return forecast