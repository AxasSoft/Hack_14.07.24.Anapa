"""empty message

Revision ID: a1eeec07074d
Revises: a0f8f615c53c
Create Date: 2023-02-21 14:30:51.153479

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1eeec07074d'
down_revision = 'a0f8f615c53c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notification', sa.Column('icon', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('notification', 'icon')
    # ### end Alembic commands ###
