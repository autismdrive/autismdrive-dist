"""empty message

Revision ID: 5a928cbc36f0
Revises: c1a41dfb42c8
Create Date: 2019-05-09 11:00:53.864448

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a928cbc36f0'
down_revision = 'c1a41dfb42c8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('location_category')
    op.drop_table('event_category')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('event_category',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('event_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('category_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], name='event_category_category_id_fkey'),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], name='event_category_event_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='event_category_pkey')
    )
    op.create_table('location_category',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('location_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('category_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], name='location_category_category_id_fkey'),
    sa.ForeignKeyConstraint(['location_id'], ['location.id'], name='location_category_location_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='location_category_pkey')
    )
    # ### end Alembic commands ###