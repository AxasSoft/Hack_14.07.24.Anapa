"""add table dislaike

Revision ID: 8b036b9bf975
Revises: f1c6084c0c00
Create Date: 2024-07-13 15:45:34.839940

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b036b9bf975'
down_revision = 'f1c6084c0c00'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('profiledislike',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('disliker_dating_profile_id', sa.Integer(), nullable=True),
    sa.Column('disliked_dating_profile_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['disliked_dating_profile_id'], ['datingprofile.id'], ),
    sa.ForeignKeyConstraint(['disliker_dating_profile_id'], ['datingprofile.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_profiledislike_id'), 'profiledislike', ['id'], unique=False)
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
    op.drop_index(op.f('ix_profiledislike_id'), table_name='profiledislike')
    op.drop_table('profiledislike')
    # ### end Alembic commands ###
