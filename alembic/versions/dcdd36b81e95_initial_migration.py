"""Initial migration

Revision ID: dcdd36b81e95
Revises: 
Create Date: 2024-11-24 09:39:50.906017

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'dcdd36b81e95'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('telegram_id', sa.String(), nullable=True),
    sa.Column('referrer_id', sa.String(), nullable=True),
    sa.Column('curator_id', sa.String(), nullable=True),
    sa.Column('key_number', sa.Integer(), nullable=True),
    sa.Column('curator_contact_visible', sa.Boolean(), nullable=True),
    sa.Column('last_curator_request', sa.Float(), nullable=True),
    sa.Column('verification_codes', postgresql.ARRAY(sa.String()), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=True)
    op.create_table('keys',
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('number')
    )
    op.create_table('referral_relationships',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('referrer_id', sa.String(), nullable=True),
    sa.Column('referral_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['referral_id'], ['users.telegram_id'], ),
    sa.ForeignKeyConstraint(['referrer_id'], ['users.telegram_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_referral_relationships_id'), 'referral_relationships', ['id'], unique=False)
    op.create_table('wallets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('type', sa.Enum('USDT_TRC20', 'BTC', 'LYC', name='wallettype'), nullable=True),
    sa.Column('address', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_wallets_id'), 'wallets', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_wallets_id'), table_name='wallets')
    op.drop_table('wallets')
    op.drop_index(op.f('ix_referral_relationships_id'), table_name='referral_relationships')
    op.drop_table('referral_relationships')
    op.drop_table('keys')
    op.drop_index(op.f('ix_users_telegram_id'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###