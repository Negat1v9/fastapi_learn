"""add foreign-key to post table

Revision ID: e200914478e7
Revises: ee9420216082
Create Date: 2023-05-28 00:45:49.378674

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e200914478e7'
down_revision = 'ee9420216082'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('owner_id', sa.Integer, nullable=False))
    op.create_foreign_key('post_users_fk', source_table='posts',
                        referent_table="users",
                        local_cols=['owner_id'], remote_cols=['id'],
                        ondelete="CASCADE")


def downgrade() -> None:
    op.drop_constraint("post_users_fk", table_name='posts')
    op.drop_column('posts', 'owner_id')