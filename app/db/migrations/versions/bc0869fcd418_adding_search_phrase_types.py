"""Adding search phrase types
Revision ID: bc0869fcd418
Revises: ebb5a3514c30
Create Date: 2022-01-25 23:03:36.217389
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'bc0869fcd418'
down_revision = 'ebb5a3514c30'
branch_labels = None
depends_on = None
def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('search_phrases', sa.Column('type', sa.Enum('title', 'summary', 'manual', name='phrase_types'), nullable=True))
    # ### end Alembic commands ###
def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('search_phrases', 'type')
    # ### end Alembic commands ###