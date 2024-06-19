"""empty message

Revision ID: 97dc2b673131
Revises: 850a3a5bad8a
Create Date: 2024-06-18 11:26:46.597850

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97dc2b673131'
down_revision = '850a3a5bad8a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('city',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('postal_code',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('address_line1',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('address_line2',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('phone',
               existing_type=sa.VARCHAR(),
               nullable=True)

    with op.batch_alter_table('stl_model', schema=None) as batch_op:
        batch_op.add_column(sa.Column('errors', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('stl_model', schema=None) as batch_op:
        batch_op.drop_column('errors')

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.alter_column('phone',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('address_line2',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('address_line1',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('postal_code',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('city',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('status',
               existing_type=sa.VARCHAR(),
               nullable=False)

    # ### end Alembic commands ###
