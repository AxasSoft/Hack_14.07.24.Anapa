"""empty message

Revision ID: db15e84ad38f
Revises: 068c91db4b1c
Create Date: 2023-02-21 12:58:13.561862

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db15e84ad38f'
down_revision = '068c91db4b1c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('body', sa.String(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('offer_id', sa.Integer(), nullable=True),
    sa.Column('stage', sa.Integer(), nullable=True),
    sa.Column('is_read', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['offer_id'], ['offer.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_body'), 'notification', ['body'], unique=False)
    op.create_index(op.f('ix_notification_created'), 'notification', ['created'], unique=False)
    op.create_index(op.f('ix_notification_id'), 'notification', ['id'], unique=False)
    op.create_index(op.f('ix_notification_is_read'), 'notification', ['is_read'], unique=False)
    op.create_index(op.f('ix_notification_offer_id'), 'notification', ['offer_id'], unique=False)
    op.create_index(op.f('ix_notification_order_id'), 'notification', ['order_id'], unique=False)
    op.create_index(op.f('ix_notification_stage'), 'notification', ['stage'], unique=False)
    op.create_index(op.f('ix_notification_title'), 'notification', ['title'], unique=False)
    op.create_index(op.f('ix_notification_user_id'), 'notification', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_notification_user_id'), table_name='notification')
    op.drop_index(op.f('ix_notification_title'), table_name='notification')
    op.drop_index(op.f('ix_notification_stage'), table_name='notification')
    op.drop_index(op.f('ix_notification_order_id'), table_name='notification')
    op.drop_index(op.f('ix_notification_offer_id'), table_name='notification')
    op.drop_index(op.f('ix_notification_is_read'), table_name='notification')
    op.drop_index(op.f('ix_notification_id'), table_name='notification')
    op.drop_index(op.f('ix_notification_created'), table_name='notification')
    op.drop_index(op.f('ix_notification_body'), table_name='notification')
    op.drop_table('notification')
    # ### end Alembic commands ###
