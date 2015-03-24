"""empty message

Revision ID: 1ed4de40bd9
Revises: 510c9758da14
Create Date: 2015-03-24 18:47:18.483771

"""

# revision identifiers, used by Alembic.
revision = '1ed4de40bd9'
down_revision = '510c9758da14'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('description', sa.String(length=500), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('project', 'description')
    ### end Alembic commands ###