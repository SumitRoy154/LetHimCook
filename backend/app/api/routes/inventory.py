import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.exceptions.base import BusinessException
from app.models.user import User
from app.schemas.api import InventoryItemResponse
from app.services.inventory_service import InventoryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get(
    "",
    response_model=List[InventoryItemResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Inventory",
    description="Return all current ingredients in the authenticated user's inventory.",
)
def get_inventory(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[InventoryItemResponse]:
    try:
        inventory_service = InventoryService(db)
        items = inventory_service.get_inventory(current_user.id)
        return [InventoryItemResponse.model_validate(item) for item in items]
    except BusinessException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        logger.exception("Error getting inventory: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred")
