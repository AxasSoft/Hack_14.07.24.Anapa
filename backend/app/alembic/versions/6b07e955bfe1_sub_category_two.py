"""sub_category_two

Revision ID: 6b07e955bfe1
Revises: f07bd506ff5d
Create Date: 2024-07-02 09:03:42.804909

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b07e955bfe1'
down_revision = 'f07bd506ff5d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('userinterest',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('interest_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['interest_id'], ['interest.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_userinterest_id'), 'userinterest', ['id'], unique=False)
    op.create_index(op.f('ix_userinterest_interest_id'), 'userinterest', ['interest_id'], unique=False)
    op.create_index(op.f('ix_userinterest_user_id'), 'userinterest', ['user_id'], unique=False)
    # op.drop_table('spatial_ref_sys')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('spatial_ref_sys',
    sa.Column('srid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('auth_name', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    sa.Column('auth_srid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('srtext', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    sa.Column('proj4text', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    sa.CheckConstraint('(srid > 0) AND (srid <= 998999)', name='spatial_ref_sys_srid_check'),
    sa.PrimaryKeyConstraint('srid', name='spatial_ref_sys_pkey')
    )
    op.drop_index(op.f('ix_userinterest_user_id'), table_name='userinterest')
    op.drop_index(op.f('ix_userinterest_interest_id'), table_name='userinterest')
    op.drop_index(op.f('ix_userinterest_id'), table_name='userinterest')
    op.drop_table('userinterest')
    # ### end Alembic commands ###
