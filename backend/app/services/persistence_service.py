import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.workflow_execution import WorkflowExecution
from app.repositories.workflow_execution_repo import WorkflowExecutionRepository

logger = logging.getLogger(__name__)


class PersistenceService:
    def __init__(self, db: Session):
        self.db = db
        self.workflow_repo = WorkflowExecutionRepository(db)

    def save_execution(
        self,
        order_id: int,
        user_id: int,
        workflow_status: str,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        execution_time_ms: Optional[int] = None,
        execution_logs: Optional[List[str]] = None,
        error_logs: Optional[List[str]] = None,
        graph_state_snapshot: Optional[Dict[str, Any]] = None,
        final_wallet_balance: Optional[Decimal] = None,
        bonus_coins: Optional[Decimal] = None,
    ) -> Optional[WorkflowExecution]:
        """Save a complete workflow execution audit record. Catches and swallows errors to prevent transaction rollback."""
        try:
            record = WorkflowExecution(
                order_id=order_id,
                user_id=user_id,
                workflow_status=workflow_status,
                started_at=started_at,
                completed_at=completed_at,
                execution_time_ms=execution_time_ms,
                execution_logs=execution_logs or [],
                error_logs=error_logs or [],
                graph_state_snapshot=graph_state_snapshot or {},
                final_wallet_balance=final_wallet_balance,
                bonus_coins=bonus_coins,
            )
            created_record = self.workflow_repo.create(record)
            logger.info("Workflow execution audit record saved | execution_id=%s, order_id=%s", created_record.id, order_id)
            return created_record
        except Exception as exc:
            self.db.rollback()
            logger.error("PersistenceService.save_execution failed (swallowed): %s", exc)
            return None

    def get_execution(self, execution_id: int) -> Optional[WorkflowExecution]:
        return self.workflow_repo.get_by_id(execution_id)

    def get_execution_history(self, user_id: int, skip: int = 0, limit: int = 50) -> List[WorkflowExecution]:
        return self.workflow_repo.get_history_by_user(user_id, skip=skip, limit=limit)
