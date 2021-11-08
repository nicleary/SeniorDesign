"""Adding bill actions and versions
Revision ID: 49c969dc1d47
Revises: 475df8e8939c
Create Date: 2021-11-08 18:00:47.014070
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
# revision identifiers, used by Alembic
revision = '49c969dc1d47'
down_revision = '475df8e8939c'
branch_labels = None
depends_on = None
def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bill_actions',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('bill', sa.String(length=16), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.Column('chamber', sa.String(length=16), nullable=False),
    sa.Column('action_type', sa.String(length=128), nullable=True),
    sa.Column('datetime', sa.DateTime(), nullable=False),
    sa.Column('description', sa.String(length=1024), nullable=True),
    sa.ForeignKeyConstraint(['bill'], ['bills.bill_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bill_verions',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('bill', sa.String(length=16), nullable=True),
    sa.Column('status', sa.String(length=64), nullable=True),
    sa.Column('title', sa.String(length=8), nullable=True),
    sa.Column('url', sa.String(length=512), nullable=True),
    sa.Column('congressdotgov_url', sa.String(length=512), nullable=True),
    sa.ForeignKeyConstraint(['bill'], ['bills.bill_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bill_verions')
    op.drop_table('bill_actions')
    # ### end Alembic commands ###