import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.exceptions.base import BusinessException
from app.graph.workflow import build_cooking_graph
from app.models.user import User
from app.repositories.workflow_execution_repo import WorkflowExecutionRepository
from app.schemas.api import (
    OrderCreateRequest,
    OrderCreateResponse,
    OrderDetailResponse,
    OrderResponse,
    ReviewResponse,
    ShoppingItemResponse,
    WorkflowExecutionSummaryResponse,
)
from app.services.order_service import OrderService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "",
    response_model=OrderCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Order",
    description="Create a new dish order and invoke the LangGraph agent workflow orchestration engine.",
)
def create_order(
    payload: OrderCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrderCreateResponse:
    try:
        order_service = OrderService(db)
        order = order_service.create_order(user_id=current_user.id, dish_name=payload.dish_name)

        # Build and invoke LangGraph graph
        graph = build_cooking_graph(db=db, mock=payload.mock)
        initial_state = {
            "order_id": order.id,
            "user_id": current_user.id,
            "dish_name": order.dish_name,
            "mock": payload.mock,
        }

        final_state = graph.invoke(initial_state)

        # Fallback to mock execution if real API quota fails
        if final_state.get("current_status") == "FAILED" and not payload.mock:
            logger.warning("Order #%s failed with real LLM provider, falling back to mock mode", order.id)
            mock_graph = build_cooking_graph(db=db, mock=True)
            retry_state = {
                "order_id": order.id,
                "user_id": current_user.id,
                "dish_name": order.dish_name,
                "mock": True,
            }
            final_state = mock_graph.invoke(retry_state)

        # Retrieve resulting workflow execution ID if saved
        workflow_repo = WorkflowExecutionRepository(db)
        executions = workflow_repo.get_by_order_id(order.id)
        execution_id = executions[0].id if executions else None


        # Refresh order to get updated status
        db.refresh(order)

        return OrderCreateResponse(
            order_id=order.id,
            workflow_execution_id=execution_id,
            status=order.status,
            message=f"Order #{order.id} processed with status: {order.status}",
        )
    except BusinessException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        logger.exception("Error processing order: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred")


@router.get(
    "",
    response_model=List[OrderResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Order History",
    description="Return historical orders for the currently authenticated user.",
)
def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[OrderResponse]:
    order_service = OrderService(db)
    orders = order_service.get_order_history(user_id=current_user.id, skip=skip, limit=limit)
    return [OrderResponse.model_validate(o) for o in orders]


@router.get(
    "/{order_id}",
    response_model=OrderDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Order Details",
    description="Return complete order details including shopping summary, judge review, cooking session, and workflow execution.",
)
def get_order_details(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrderDetailResponse:
    try:
        order_service = OrderService(db)
        order = order_service.get_order_details(order_id)

        if order.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this order")

        # Gather shopping items
        shopping_summary = [ShoppingItemResponse.model_validate(item) for item in order.shopping_items]

        # Gather judge review
        judge_review = ReviewResponse.model_validate(order.review) if order.review else None

        # Gather workflow execution
        workflow_repo = WorkflowExecutionRepository(db)
        executions = workflow_repo.get_by_order_id(order.id)
        workflow_execution = (
            WorkflowExecutionSummaryResponse.model_validate(executions[0]) if executions else None
        )

        # Gather cooking session state if present in execution snapshot
        cooking_session = None
        if executions and executions[0].graph_state_snapshot:
            cooking_session = executions[0].graph_state_snapshot.get("cook_response")

        return OrderDetailResponse(
            id=order.id,
            user_id=order.user_id,
            dish_name=order.dish_name,
            status=order.status,
            total_cost=order.total_cost,
            reward_received=order.reward_received,
            created_at=order.created_at,
            shopping_summary=shopping_summary,
            cooking_session=cooking_session,
            judge_review=judge_review,
            wallet_reward=order.reward_received,
            workflow_execution=workflow_execution,
        )
    except BusinessException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting order details: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred")
