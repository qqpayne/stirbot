"""place additions

Revision ID: df03c8014a1b
Revises: 709877c3d0a1
Create Date: 2024-08-22 00:18:47.901854

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "df03c8014a1b"
down_revision: str | None = "709877c3d0a1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("places", sa.Column("comment", sa.String(), server_default="", nullable=False))
    op.add_column("places", sa.Column("daily_quota_minutes", sa.Integer(), nullable=True))
    op.add_column(
        "places", sa.Column("minimal_interval_minutes", sa.Integer(), server_default=sa.text("0"), nullable=False)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("places", "minimal_interval_minutes")
    op.drop_column("places", "daily_quota_minutes")
    op.drop_column("places", "comment")
    # ### end Alembic commands ###
