"""Add new columns

Revision ID: a7a97b835b79
Revises: 9c6fa67a1036
Create Date: 2020-08-18 18:29:53.800143

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7a97b835b79'
down_revision = '9c6fa67a1036'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('articles', sa.Column('abstract', sa.Text(), nullable=True))
    op.add_column('articles', sa.Column('abstract_len', sa.Integer(), nullable=True))
    op.add_column('articles', sa.Column('affiliations', sa.Text(), nullable=True))
    op.add_column('articles', sa.Column('article_type', sa.String(length=30), nullable=True))
    op.add_column('articles', sa.Column('authors', sa.Text(), nullable=True))
    op.add_column('articles', sa.Column('copyright', sa.Text(), nullable=True))
    op.add_column('articles', sa.Column('file_size', sa.Integer(), nullable=True))
    op.add_column('articles', sa.Column('issn_electronic', sa.String(length=30), nullable=True))
    op.add_column('articles', sa.Column('issn_print', sa.String(length=30), nullable=True))
    op.add_column('articles', sa.Column('issue', sa.String(length=100), nullable=True))
    op.add_column('articles', sa.Column('journal_iso_abbr', sa.String(length=150), nullable=True))
    op.add_column('articles', sa.Column('journal_title', sa.Text(), nullable=True))
    op.add_column('articles', sa.Column('keywords', sa.Text(), nullable=True))
    op.add_column('articles', sa.Column('mesh_descriptors', sa.Text(), nullable=True))
    op.add_column('articles', sa.Column('mesh_quals_major', sa.Text(), nullable=True))
    op.add_column('articles', sa.Column('mesh_quals_minor', sa.Text(), nullable=True))
    op.add_column('articles', sa.Column('pages', sa.String(length=150), nullable=True))
    op.add_column('articles', sa.Column('pub_date', sa.String(length=100), nullable=True))
    op.add_column('articles', sa.Column('publication_type', sa.Text(), nullable=True))
    op.add_column('articles', sa.Column('publisher_issn_linking', sa.String(length=30), nullable=True))
    op.add_column('articles', sa.Column('publisher_location', sa.String(length=100), nullable=True))
    op.add_column('articles', sa.Column('publisher_name', sa.String(length=150), nullable=True))
    op.add_column('articles', sa.Column('publisher_nlm_id', sa.String(length=30), nullable=True))
    op.add_column('articles', sa.Column('volume', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('articles', 'volume')
    op.drop_column('articles', 'publisher_nlm_id')
    op.drop_column('articles', 'publisher_name')
    op.drop_column('articles', 'publisher_location')
    op.drop_column('articles', 'publisher_issn_linking')
    op.drop_column('articles', 'publication_type')
    op.drop_column('articles', 'pub_date')
    op.drop_column('articles', 'pages')
    op.drop_column('articles', 'mesh_quals_minor')
    op.drop_column('articles', 'mesh_quals_major')
    op.drop_column('articles', 'mesh_descriptors')
    op.drop_column('articles', 'keywords')
    op.drop_column('articles', 'journal_title')
    op.drop_column('articles', 'journal_iso_abbr')
    op.drop_column('articles', 'issue')
    op.drop_column('articles', 'issn_print')
    op.drop_column('articles', 'issn_electronic')
    op.drop_column('articles', 'file_size')
    op.drop_column('articles', 'copyright')
    op.drop_column('articles', 'authors')
    op.drop_column('articles', 'article_type')
    op.drop_column('articles', 'affiliations')
    op.drop_column('articles', 'abstract_len')
    op.drop_column('articles', 'abstract')
    # ### end Alembic commands ###
