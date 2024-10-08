"""user notifications

Revision ID: f416c42e5f5b
Revises: df03c8014a1b
Create Date: 2024-08-22 08:28:54.575496

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f416c42e5f5b"
down_revision: str | None = "df03c8014a1b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("notify_before_start_mins", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("notify_before_end_mins", sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "notify_before_end_mins")
    op.drop_column("users", "notify_before_start_mins")
    # ### end Alembic commands ###
