import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.exceptions.base import BusinessException
from app.models.order import Order
from app.models.review import Review
from app.models.user import User
from app.schemas.api import ReviewResponse
from app.services.review_memory_service import ReviewMemoryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get(
    "",
    response_model=List[ReviewResponse],
    status_code=status.HTTP_200_OK,
    summary="Get User Reviews",
    description="Return all reviews for orders placed by the authenticated user.",
)
def get_user_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[ReviewResponse]:
    try:
        stmt = (
            select(Review)
            .join(Order, Review.order_id == Order.id)
            .where(Order.user_id == current_user.id)
            .order_by(Review.created_at.desc())
        )
        reviews = list(db.scalars(stmt).all())
        return [ReviewResponse.model_validate(r) for r in reviews]
    except BusinessException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        logger.exception("Error getting reviews: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred")


@router.get(
    "/{dish_name}",
    response_model=List[str],
    status_code=status.HTTP_200_OK,
    summary="Get Previous Dish Suggestions",
    description="Return previous suggestions and feedback for a specific dish.",
)
def get_dish_suggestions(
    dish_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[str]:
    try:
        review_service = ReviewMemoryService(db)
        suggestions = review_service.get_previous_suggestions(dish_name=dish_name)
        return suggestions
    except BusinessException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        logger.exception("Error getting dish suggestions: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred")
