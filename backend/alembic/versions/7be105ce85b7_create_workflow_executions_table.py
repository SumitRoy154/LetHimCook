"""create_workflow_executions_table

Revision ID: 7be105ce85b7
Revises: f948429ddcc8
Create Date: 2026-07-30 23:44:10.249766

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7be105ce85b7'
down_revision: Union[str, None] = 'f948429ddcc8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('workflow_executions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('workflow_status', sa.String(length=50), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('execution_time_ms', sa.Integer(), nullable=True),
    sa.Column('execution_logs', sa.JSON(), nullable=True),
    sa.Column('error_logs', sa.JSON(), nullable=True),
    sa.Column('graph_state_snapshot', sa.JSON(), nullable=True),
    sa.Column('final_wallet_balance', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('bonus_coins', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_executions_id'), 'workflow_executions', ['id'], unique=False)
    op.create_index(op.f('ix_workflow_executions_order_id'), 'workflow_executions', ['order_id'], unique=False)
    op.create_index(op.f('ix_workflow_executions_user_id'), 'workflow_executions', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_workflow_executions_user_id'), table_name='workflow_executions')
    op.drop_index(op.f('ix_workflow_executions_order_id'), table_name='workflow_executions')
    op.drop_index(op.f('ix_workflow_executions_id'), table_name='workflow_executions')
    op.drop_table('workflow_executions')
