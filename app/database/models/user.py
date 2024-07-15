from aiogram.utils.link import create_tg_link
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, big_int_pk, created_at


class User(Base):
    id: Mapped[big_int_pk]
    first_name: Mapped[str]
    last_name: Mapped[str | None]
    username: Mapped[str | None]
    created_at: Mapped[created_at]

    is_admin: Mapped[bool] = mapped_column(default=False)
    is_approved: Mapped[bool] = mapped_column(default=False)

    @property
    def full_name(self) -> str:
        if self.last_name is not None:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    @property
    def clickable_name(self) -> str:
        name_with_link = f"<a href='{create_tg_link('user', id=self.id)}'>{self.full_name}</a>"
        if self.username is not None:
            return f"{name_with_link} (@{self.username})"
        return name_with_link

    def __repr__(self) -> str:
        if self.username is not None:
            return f"{self.full_name} (@{self.username}, id:{self.id})"
        return f"{self.full_name} (id:{self.id})"
