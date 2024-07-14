"""empty message

Revision ID: b8a7c078d463
Revises: 636580f2f97b
Create Date: 2023-09-29 12:19:04.573375

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8a7c078d463'
down_revision = '636580f2f97b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('profile_photo', sa.String(), nullable=True))
    op.add_column('user', sa.Column('status', sa.String(), nullable=True))
    op.add_column('user', sa.Column('subscriptions_count', sa.Integer(), server_default='0', nullable=False))
    op.add_column('user', sa.Column('subscribers_count', sa.Integer(), server_default='0', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'subscribers_count')
    op.drop_column('user', 'subscriptions_count')
    op.drop_column('user', 'status')
    op.drop_column('user', 'profile_photo')
    op.create_table('spatial_ref_sys',
    sa.Column('srid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('auth_name', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    sa.Column('auth_srid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('srtext', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    sa.Column('proj4text', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    sa.CheckConstraint('(srid > 0) AND (srid <= 998999)', name='spatial_ref_sys_srid_check'),
    sa.PrimaryKeyConstraint('srid', name='spatial_ref_sys_pkey')
    )
    # ### end Alembic commands ###
