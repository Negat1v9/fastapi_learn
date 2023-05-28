"""Added content column

Revision ID: 04185b87c2b3
Revises: 9dfd26059850
Create Date: 2023-05-28 00:29:27.483327

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04185b87c2b3'
down_revision = '9dfd26059850'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))


def downgrade() -> None:
    op.drop_column('posts', 'content')
