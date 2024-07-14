"""empty message

Revision ID: e8d626c9a8b5
Revises: 781d918884e4
Create Date: 2023-08-21 12:11:49.471977

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8d626c9a8b5'
down_revision = '781d918884e4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('lat', sa.Float(), nullable=True))
    op.add_column('order', sa.Column('lon', sa.Float(), nullable=True))
    op.add_column('user', sa.Column('lat', sa.Float(), nullable=True))
    op.add_column('user', sa.Column('lon', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'lon')
    op.drop_column('user', 'lat')
    op.drop_column('order', 'lon')
    op.drop_column('order', 'lat')
    # ### end Alembic commands ###
