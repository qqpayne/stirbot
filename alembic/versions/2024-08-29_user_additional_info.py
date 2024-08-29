"""user additional info

Revision ID: 24bec65e268f
Revises: f416c42e5f5b
Create Date: 2024-08-29 21:32:54.703151

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "24bec65e268f"
down_revision: str | None = "f416c42e5f5b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("additional_info", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "additional_info")
    # ### end Alembic commands ###