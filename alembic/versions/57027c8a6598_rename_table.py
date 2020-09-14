"""Rename table

Revision ID: 57027c8a6598
Revises: 49b837b0192a
Create Date: 2020-09-14 16:07:37.812144

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '57027c8a6598'
down_revision = '49b837b0192a'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('articles', 'pubmed')


def downgrade():
    op.rename_table('pubmed', 'articles')
