from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, JSON, func
from sqlalchemy.orm import relationship

from app.models.base import Base


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workflow_status = Column(String(50), nullable=False, default="PENDING")
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    execution_logs = Column(JSON, nullable=True)
    error_logs = Column(JSON, nullable=True)
    graph_state_snapshot = Column(JSON, nullable=True)
    final_wallet_balance = Column(Numeric(12, 2), nullable=True)
    bonus_coins = Column(Numeric(12, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    order = relationship("Order", backref="workflow_executions")
    user = relationship("User", backref="workflow_executions")
