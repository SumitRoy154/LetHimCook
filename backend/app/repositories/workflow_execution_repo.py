import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workflow_execution import WorkflowExecution
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class WorkflowExecutionRepository(BaseRepository[WorkflowExecution]):
    def __init__(self, db: Session):
        super().__init__(WorkflowExecution, db)

    def get_by_order_id(self, order_id: int) -> List[WorkflowExecution]:
        stmt = (
            select(WorkflowExecution)
            .where(WorkflowExecution.order_id == order_id)
            .order_by(WorkflowExecution.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_history_by_user(self, user_id: int, skip: int = 0, limit: int = 50) -> List[WorkflowExecution]:
        stmt = (
            select(WorkflowExecution)
            .where(WorkflowExecution.user_id == user_id)
            .order_by(WorkflowExecution.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
