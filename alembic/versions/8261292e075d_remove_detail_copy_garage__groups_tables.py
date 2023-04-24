"""remove (detail_copy|garage)_groups tables

Revision ID: 8261292e075d
Revises: 783a091df9a2
Create Date: 2023-04-24 11:47:05.569886

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8261292e075d'
down_revision = '783a091df9a2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('garage_groups')
    op.drop_table('detail_copy_groups')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('detail_copy_groups',
    sa.Column('detail_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('ship_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['detail_id'], ['details_copies.id'], name='detail_copy_groups_detail_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['ship_id'], ['ships.id'], name='detail_copy_groups_ship_id_fkey', ondelete='CASCADE')
    )
    op.create_table('garage_groups',
    sa.Column('garage_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('detail_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['detail_id'], ['details_copies.id'], name='garage_groups_detail_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['garage_id'], ['garages.id'], name='garage_groups_garage_id_fkey', ondelete='CASCADE')
    )
    # ### end Alembic commands ###