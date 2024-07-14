"""empty message

Revision ID: d57c613e1317
Revises: a14d3a957cc2
Create Date: 2023-01-22 11:10:59.442847

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd57c613e1317'
down_revision = 'a14d3a957cc2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_category_name', table_name='category')
    op.create_index(op.f('ix_category_name'), 'category', ['name'], unique=False)
    op.drop_index('ix_subcategory_name', table_name='subcategory')
    op.create_index(op.f('ix_subcategory_name'), 'subcategory', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_subcategory_name'), table_name='subcategory')
    op.create_index('ix_subcategory_name', 'subcategory', ['name'], unique=False)
    op.drop_index(op.f('ix_category_name'), table_name='category')
    op.create_index('ix_category_name', 'category', ['name'], unique=False)
    # ### end Alembic commands ###
