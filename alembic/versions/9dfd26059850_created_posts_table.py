"""created posts table

Revision ID: 9dfd26059850
Revises: 
Create Date: 2023-05-28 00:28:07.767771

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9dfd26059850'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("posts", sa.Column('id', sa.Integer, nullable=False,
                            primary_key=True), sa.Column('title', sa.String(),
                            nullable=False))


def downgrade() -> None:
    op.drop_table('posts')
