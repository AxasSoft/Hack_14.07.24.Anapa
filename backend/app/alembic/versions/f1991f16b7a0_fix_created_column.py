"""fix created column

Revision ID: f1991f16b7a0
Revises: 2831a40e755c
Create Date: 2022-06-08 07:12:44.010917

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1991f16b7a0'
down_revision = '2831a40e755c'
branch_labels = None
depends_on = None


def upgrade():
    return None
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('device', 'created',
               existing_type=sa.VARCHAR(),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.alter_column('firebasetoken', 'created',
               existing_type=sa.VARCHAR(),
               type_=sa.DateTime(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    return None
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('firebasetoken', 'created',
               existing_type=sa.DateTime(),
               type_=sa.VARCHAR(),
               existing_nullable=False)
    op.alter_column('device', 'created',
               existing_type=sa.DateTime(),
               type_=sa.VARCHAR(),
               existing_nullable=False)
    # ### end Alembic commands ###
