"""initial

Revision ID: 0954784169b6
Revises: 
Create Date: 2019-07-21 16:42:24.291503

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '0954784169b6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('action',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('order', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('user',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('registration',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('action_id', sa.Integer(), nullable=False),
                    sa.Column('timestamp_start', sa.Integer(), nullable=False),
                    sa.Column('timestamp_end', sa.Integer(), nullable=True),
                    sa.Column('elapsed', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['action_id'], ['action.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('registration')
    op.drop_table('user')
    op.drop_table('action')
   