"""empty message

Revision ID: c471027d2bcf
Revises: 543fb224b6c6
Create Date: 2023-01-21 16:42:37.406732

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c471027d2bcf'
down_revision = '543fb224b6c6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('body', sa.String(), nullable=True),
    sa.Column('category', sa.Integer(), nullable=False),
    sa.Column('image', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_info_created'), 'info', ['created'], unique=False)
    op.create_index(op.f('ix_info_id'), 'info', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_info_id'), table_name='info')
    op.drop_index(op.f('ix_info_created'), table_name='info')
    op.drop_table('info')
    # ### end Alembic commands ###
