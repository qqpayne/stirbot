from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, big_int_pk, created_at


class User(Base):
    id: Mapped[big_int_pk]
    first_name: Mapped[str]
    last_name: Mapped[str | None]
    username: Mapped[str | None]
    created_at: Mapped[created_at]

    is_admin: Mapped[bool] = mapped_column(default=False)
