import logging
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.review import ReviewNotFoundException
from app.models.order import Order
from app.models.review import Review
from app.repositories.review_repo import ReviewRepository

logger = logging.getLogger(__name__)


class ReviewMemoryService:
    def __init__(self, db: Session):
        self.db = db
        self.review_repo = ReviewRepository(db)

    def search_reviews(self, order_id: int) -> Optional[Review]:
        """Fetch review record for a specific order."""
        return self.review_repo.get_by_order_id(order_id)

    def store_review(
        self,
        order_id: int,
        score: Decimal,
        review_text: str,
        suggestions: Optional[str] = None,
        bonus_coins: Decimal = Decimal("0.00"),
    ) -> Review:
        """Store evaluation review details for an order (used by Judge role)."""
        existing = self.review_repo.get_by_order_id(order_id)
        if existing:
            existing.score = score
            existing.review = review_text
            existing.suggestions = suggestions
            existing.bonus_coins = bonus_coins
            updated = self.review_repo.update(existing)
            logger.info("Review updated | order_id=%s, review_id=%s", order_id, updated.id)
            return updated

        new_review = Review(
            order_id=order_id,
            score=score,
            review=review_text,
            suggestions=suggestions,
            bonus_coins=bonus_coins,
        )
        created = self.review_repo.create(new_review)
        logger.info("Review stored in memory | order_id=%s, score=%s, review_id=%s", order_id, score, created.id)
        return created

    def get_previous_suggestions(self, dish_name: str, limit: int = 5) -> List[str]:
        """Fetch historical cooking improvement suggestions for a dish name (used by Cook role)."""
        normalized_name = dish_name.lower().strip()
        stmt = (
            select(Review.suggestions)
            .join(Order, Review.order_id == Order.id)
            .where(
                Order.dish_name.ilike(f"%{normalized_name}%"),
                Review.suggestions.isnot(None),
                Review.suggestions != "",
            )
            .order_by(Review.created_at.desc())
            .limit(limit)
        )
        results = list(self.db.scalars(stmt).all())
        logger.info("Retrieved %s historical suggestions for dish '%s'", len(results), normalized_name)
        return [s for s in results if s]
