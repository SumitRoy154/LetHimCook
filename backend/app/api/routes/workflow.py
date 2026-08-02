import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.exceptions.base import BusinessException
from app.models.user import User
from app.schemas.api import WorkflowExecutionDetailResponse, WorkflowExecutionSummaryResponse
from app.services.persistence_service import PersistenceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflow", tags=["Workflow Engine"])


@router.get(
    "/history",
    response_model=List[WorkflowExecutionSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Workflow History",
    description="Return all workflow executions for the authenticated user.",
)
def get_workflow_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[WorkflowExecutionSummaryResponse]:
    try:
        persistence_service = PersistenceService(db)
        history = persistence_service.get_execution_history(user_id=current_user.id, skip=skip, limit=limit)
        return [WorkflowExecutionSummaryResponse.model_validate(item) for item in history]
    except BusinessException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        logger.exception("Error getting workflow history: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred")


@router.get(
    "/{execution_id}",
    response_model=WorkflowExecutionDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Workflow Execution Details",
    description="Return detailed execution logs, snapshot, duration, status, and errors for a specific workflow execution.",
)
def get_workflow_execution(
    execution_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkflowExecutionDetailResponse:
    try:
        persistence_service = PersistenceService(db)
        execution = persistence_service.get_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow execution #{execution_id} not found")

        if execution.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this workflow execution")

        return WorkflowExecutionDetailResponse.model_validate(execution)
    except BusinessException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting workflow execution detail: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred")
