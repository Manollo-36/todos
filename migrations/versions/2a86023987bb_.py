"""empty message

Revision ID: 2a86023987bb
Revises: 2c66a2eadb6c
Create Date: 2024-10-14 15:51:43.495914

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a86023987bb'
down_revision = '2c66a2eadb6c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('todos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('list_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'todolists', ['list_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('todos', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('list_id')

    # ### end Alembic commands ###
