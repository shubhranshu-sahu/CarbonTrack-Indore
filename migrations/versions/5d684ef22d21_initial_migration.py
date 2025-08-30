"""Initial migration

Revision ID: 5d684ef22d21
Revises: 
Create Date: 2025-08-30 15:58:54.248597

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '5d684ef22d21'
down_revision = None
branch_labels = None
depends_on = None



def upgrade():
    # ### Create users table ###
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('business_name', sa.String(length=100), nullable=False),
        sa.Column('owner_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=120), unique=True, nullable=False),
        sa.Column('password', sa.String(length=128), nullable=False),
        sa.Column('msme_category', sa.String(length=10), nullable=False),
        sa.Column('business_type', sa.String(length=100), nullable=False),
        sa.Column('sector', sa.String(length=100), nullable=False),
        sa.Column('annual_turnover', sa.Float(), nullable=True),
        sa.Column('location', sa.String(length=150), nullable=True),
        sa.Column('contact_number', sa.String(length=15), nullable=True),
        sa.Column('registration_number', sa.String(length=50), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(),
            nullable=True,
            server_default=sa.text('CURRENT_TIMESTAMP')
        ),
    )

    # ### Create sector_limits table ###
    op.create_table(
        'sector_limits',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('business_type', sa.String(length=100), nullable=True),
        sa.Column('sector', sa.String(length=100), nullable=True),
        sa.Column(
            'msme_category',
            sa.Enum('Micro', 'Small', 'Medium', name='msme_category_enum'),
            nullable=True
        ),
        sa.Column('yearly_limit_tco2', sa.Integer(), nullable=True),
        sa.Column('last_updated', sa.Date(), nullable=True),
    )

    # ### Create emissions table ###
    op.create_table(
        'emissions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('sub_type', sa.String(length=50), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=20), nullable=False),
        sa.Column('emission', sa.Float(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade():
    # Drop emissions first due to FK constraint
    op.drop_table('emissions')
    op.drop_table('sector_limits')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS msme_category_enum')