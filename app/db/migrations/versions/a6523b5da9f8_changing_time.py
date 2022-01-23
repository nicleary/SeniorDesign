"""Changing time
Revision ID: a6523b5da9f8
Revises: d59e0702753e
Create Date: 2022-01-23 06:14:03.488820
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
# revision identifiers, used by Alembic
revision = 'a6523b5da9f8'
down_revision = 'd59e0702753e'
branch_labels = None
depends_on = None
def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('bills', 'latest_major_action_date',
               existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=32),
               type_=sa.Date(),
               existing_nullable=True)
    # ### end Alembic commands ###
def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('bills', 'latest_major_action_date',
               existing_type=sa.Date(),
               type_=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=32),
               existing_nullable=True)
    # ### end Alembic commands ###