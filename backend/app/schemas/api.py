from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ----------------------------------------------------
# Order Schemas
# ----------------------------------------------------
class OrderCreateRequest(BaseModel):
    dish_name: str = Field(..., min_length=1, max_length=150, example="Spaghetti Carbonara")
    mock: bool = Field(default=False, description="Whether to run the graph in mock mode if API limits occur")


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    dish_name: str
    status: str
    total_cost: Decimal
    reward_received: Decimal
    created_at: datetime


class OrderCreateResponse(BaseModel):
    order_id: int
    workflow_execution_id: Optional[int] = None
    status: str
    message: str = "Order created and workflow executed"


class ShoppingItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ingredient_name: str
    quantity: Decimal
    unit: str = "item"
    price: Decimal


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    score: Decimal
    review: str
    suggestions: Optional[str] = None
    bonus_coins: Decimal
    created_at: datetime


class WorkflowExecutionSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    workflow_status: str
    execution_time_ms: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime


class OrderDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    dish_name: str
    status: str
    total_cost: Decimal
    reward_received: Decimal
    created_at: datetime
    shopping_summary: List[ShoppingItemResponse] = []
    cooking_session: Optional[Dict[str, Any]] = None
    judge_review: Optional[ReviewResponse] = None
    wallet_reward: Decimal = Decimal("0.00")
    workflow_execution: Optional[WorkflowExecutionSummaryResponse] = None


# ----------------------------------------------------
# Wallet & Transaction Schemas
# ----------------------------------------------------
class WalletBalanceResponse(BaseModel):
    balance: Decimal = Field(..., example=1000.00)


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    wallet_id: int
    amount: Decimal
    transaction_type: str
    description: Optional[str] = None
    created_at: datetime


# ----------------------------------------------------
# Inventory Schemas
# ----------------------------------------------------
class InventoryItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    ingredient_name: str
    quantity: Decimal
    unit: str
    purchase_price: Decimal
    created_at: datetime


# ----------------------------------------------------
# Workflow Schemas
# ----------------------------------------------------
class WorkflowExecutionDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    user_id: int
    workflow_status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_ms: Optional[int] = None
    execution_logs: List[str] = []
    error_logs: List[str] = []
    graph_state_snapshot: Dict[str, Any] = {}
    final_wallet_balance: Optional[Decimal] = None
    bonus_coins: Optional[Decimal] = None
    created_at: datetime


# ----------------------------------------------------
# Recipe Schemas
# ----------------------------------------------------
class RecipeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dish_name: str
    recipe_json: Dict[str, Any]
    ingredients_json: Dict[str, Any]
    estimated_cooking_time: Optional[int] = None
    created_at: datetime
