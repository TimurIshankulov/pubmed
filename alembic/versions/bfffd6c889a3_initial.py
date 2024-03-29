"""Initial

Revision ID: bfffd6c889a3
Revises: 
Create Date: 2020-08-18 11:26:14.686698

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bfffd6c889a3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('articles', sa.Column('elocation_id', sa.String(length=100), nullable=True))
    op.add_column('articles', sa.Column('language', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('articles', 'language')
    op.drop_column('articles', 'elocation_id')
    # ### end Alembic commands ###
