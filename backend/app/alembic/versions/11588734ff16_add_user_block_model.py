"""add user block model

Revision ID: 11588734ff16
Revises: 7562293249ec
Create Date: 2022-08-02 12:08:16.070233

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11588734ff16'
down_revision = '7562293249ec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('userblock',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('subject_id', sa.Integer(), nullable=True),
    sa.Column('object_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['object_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['subject_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_userblock_id'), 'userblock', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_userblock_id'), table_name='userblock')
    op.drop_table('userblock')
    # ### end Alembic commands ###
