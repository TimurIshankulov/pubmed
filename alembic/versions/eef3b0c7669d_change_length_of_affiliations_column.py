"""Change length of affiliations column

Revision ID: eef3b0c7669d
Revises: 83412109be60
Create Date: 2020-08-25 19:18:16.736020

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'eef3b0c7669d'
down_revision = '83412109be60'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('articles', 'affiliations',
               existing_type=mysql.TEXT(),
               type_=mysql.MEDIUMTEXT(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('articles', 'affiliations',
               existing_type=mysql.MEDIUMTEXT(),
               type_=mysql.TEXT(),
               existing_nullable=True)
    # ### end Alembic commands ###