"""fix members limit in group

Revision ID: 5256f99b5c05
Revises: a52587e1218e
Create Date: 2022-05-26 13:40:21.657826

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5256f99b5c05'
down_revision = 'a52587e1218e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('group_members_limit_fkey', 'group', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('group_members_limit_fkey', 'group', 'topic', ['members_limit'], ['id'])
    # ### end Alembic commands ###
