from typing import List, Dict, Optional
from datetime import datetime, timedelta
import numpy as np
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
from app.models.card import Card
from app.models.review import ReviewLog
from app.models.user import User
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self):
        # Lazy load the sentence transformer model
        self._model = None

    @property
    def model(self):
        if self._model is None:
            try:
                self._model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                logger.error(f"Failed to load sentence transformer: {e}")
                self._model = None
        return self._model

    async def detect_weak_topics(
            self,
            user: User,
            min_lapses: int = 3,
            min_cards: int = 3
    ) -> List[Dict]:
        """Detect weak topics using AI-driven pattern recognition"""
        # Get cards with high lapse count
        weak_cards = await Card.find({
            "owner.id": str(user.id),
            "lapses": {"$gte": min_lapses}
        }).to_list()

        if len(weak_cards) < min_cards:
            return []

        # Group by topic
        topic_stats = {}
        for card in weak_cards:
            topic = card.topic or "Uncategorized"
            if topic not in topic_stats:
                topic_stats[topic] = {
                    "topic": topic,
                    "cards": [],
                    "total_lapses": 0,
                    "total_ratings": 0,
                    "count": 0
                }

            topic_stats[topic]["cards"].append(card)
            topic_stats[topic]["total_lapses"] += card.lapses
            topic_stats[topic]["total_ratings"] += card.reps  # Approximation
            topic_stats[topic]["count"] += 1

        # Calculate mastery levels
        weak_topics = []
        for topic, stats in topic_stats.items():
            avg_lapses = stats["total_lapses"] / stats["count"]
            avg_rating = stats["total_ratings"] / (stats["total_lapses"] + stats["total_ratings"])
            mastery = 1 - (stats["total_lapses"] / (stats["total_lapses"] + stats["total_ratings"]))

            if mastery < 0.7:  # Below 70% mastery
                weak_topics.append({
                    "topic": topic,
                    "card_count": stats["count"],
                    "average_lapses": round(avg_lapses, 2),
                    "average_rating": round(avg_rating, 2),
                    "mastery_level": round(mastery * 100, 1)
                })

        # Sort by mastery level (weakest first)
        weak_topics.sort(key=lambda x: x["mastery_level"])

        return weak_topics[:5]

    async def get_study_stats(
            self,
            user: User,
            days: int = 30
    ) -> Dict:
        """Get comprehensive study statistics"""
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get reviews in date range
        reviews = await ReviewLog.find({
            "user.id": str(user.id),
            "review_date": {"$gte": start_date}
        }).to_list()

        if not reviews:
            return {}

        # Calculate statistics
        total_reviews = len(reviews)
        avg_rating = np.mean([r.rating for r in reviews])
        avg_time = np.mean([r.response_time for r in reviews])

        # Daily review counts
        daily_counts = {}
        for review in reviews:
            day = review.review_date.strftime("%Y-%m-%d")
            daily_counts[day] = daily_counts.get(day, 0) + 1

        # Rating distribution
        rating_dist = {1: 0, 2: 0, 3: 0, 4: 0}
        for review in reviews:
            rating_dist[review.rating] += 1

        # Retention over time
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
            "total_cards": await Card.find({"owner.id": str(user.id)}).count(),
            "streak": user.streak,
            "longest_streak": user.longest_streak
        }

    async def get_review_forecast(
            self,
            user: User,
            days: int = 30
    ) -> List[Dict]:
        """Predict upcoming review load"""
        forecast = []
        now = datetime.utcnow()

        for day in range(1, days + 1):
            date = now + timedelta(days=day)

            # Count cards due on this date
            due_count = await Card.find({
                "owner.id": str(user.id),
                "due_date": {
                    "$gte": date.replace(hour=0, minute=0, second=0),
                    "$lt": (date + timedelta(days=1)).replace(hour=0, minute=0, second=0)
                }
            }).count()

            forecast.append({
                "date": date.strftime("%Y-%m-%d"),
                "due_count": due_count
            })

        return forecast