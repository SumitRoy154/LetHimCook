"""initial_database_schema

Revision ID: f948429ddcc8
Revises: 
Create Date: 2026-07-30 21:53:34.111949

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f948429ddcc8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)

    # 2. wallets
    op.create_table(
        'wallets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('balance', sa.Numeric(precision=12, scale=2), nullable=False, server_default='100.00'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_wallets_user_id', 'wallets', ['user_id'], unique=True)

    # 3. inventories
    op.create_table(
        'inventories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('ingredient_name', sa.String(length=100), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('unit', sa.String(length=20), nullable=False),
        sa.Column('purchase_price', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_inventories_user_id', 'inventories', ['user_id'], unique=False)
    op.create_index('ix_inventories_ingredient_name', 'inventories', ['ingredient_name'], unique=False)

    # 4. orders
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('dish_name', sa.String(length=150), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('total_cost', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('reward_received', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_orders_user_id', 'orders', ['user_id'], unique=False)
    op.create_index('ix_orders_dish_name', 'orders', ['dish_name'], unique=False)
    op.create_index('ix_orders_created_at', 'orders', ['created_at'], unique=False)

    # 5. shopping_histories
    op.create_table(
        'shopping_histories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('ingredient_name', sa.String(length=100), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('purchased_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_shopping_histories_order_id', 'shopping_histories', ['order_id'], unique=False)

    # 6. transactions
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('wallet_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_transactions_wallet_id', 'transactions', ['wallet_id'], unique=False)
    op.create_index('ix_transactions_created_at', 'transactions', ['created_at'], unique=False)

    # 7. cooking_sessions
    op.create_table(
        'cooking_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('cooking_json', sa.JSON(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cooking_sessions_order_id', 'cooking_sessions', ['order_id'], unique=True)

    # 8. reviews
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column('review', sa.Text(), nullable=False),
        sa.Column('suggestions', sa.Text(), nullable=True),
        sa.Column('bonus_coins', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_reviews_order_id', 'reviews', ['order_id'], unique=True)

    # 9. recipes
    op.create_table(
        'recipes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('dish_name', sa.String(length=150), nullable=False),
        sa.Column('recipe_json', sa.JSON(), nullable=False),
        sa.Column('ingredients_json', sa.JSON(), nullable=False),
        sa.Column('estimated_cooking_time', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_recipes_dish_name', 'recipes', ['dish_name'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_recipes_dish_name', table_name='recipes')
    op.drop_table('recipes')

    op.drop_index('ix_reviews_order_id', table_name='reviews')
    op.drop_table('reviews')

    op.drop_index('ix_cooking_sessions_order_id', table_name='cooking_sessions')
    op.drop_table('cooking_sessions')

    op.drop_index('ix_transactions_created_at', table_name='transactions')
    op.drop_index('ix_transactions_wallet_id', table_name='transactions')
    op.drop_table('transactions')

    op.drop_index('ix_shopping_histories_order_id', table_name='shopping_histories')
    op.drop_table('shopping_histories')

    op.drop_index('ix_orders_created_at', table_name='orders')
    op.drop_index('ix_orders_dish_name', table_name='orders')
    op.drop_index('ix_orders_user_id', table_name='orders')
    op.drop_table('orders')

    op.drop_index('ix_inventories_ingredient_name', table_name='inventories')
    op.drop_index('ix_inventories_user_id', table_name='inventories')
    op.drop_table('inventories')

    op.drop_index('ix_wallets_user_id', table_name='wallets')
    op.drop_table('wallets')

    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
