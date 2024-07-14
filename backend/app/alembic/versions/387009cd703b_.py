"""empty message

Revision ID: 387009cd703b
Revises: 6c5eb5dc73ba
Create Date: 2023-09-20 13:05:38.744368

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '387009cd703b'
down_revision = '6c5eb5dc73ba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('event', 'started',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.add_column('user', sa.Column('is_compatriot', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
