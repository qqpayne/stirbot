from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, big_int_pk, created_at

if TYPE_CHECKING:
    from .booking import Booking


class User(Base):
    id: Mapped[big_int_pk]
    first_name: Mapped[str]
    last_name: Mapped[str | None]
    username: Mapped[str | None]
    created_at: Mapped[created_at]

    is_admin: Mapped[bool] = mapped_column(default=False)
    is_approved: Mapped[bool] = mapped_column(default=False)

    notify_before_start_mins: Mapped[int | None] = mapped_column(nullable=True, default=None)
    notify_before_end_mins: Mapped[int | None] = mapped_column(nullable=True, default=None)

    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")

    @property
    def full_name(self) -> str:
        if self.last_name is not None:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    @property
    def clickable_name(self) -> str:
        if self.username is not None:
            return f"{self.full_name} (@{self.username})"
        return self.full_name

    def __repr__(self) -> str:
        if self.username is not None:
            return f"{self.full_name} (@{self.username}, id:{self.id})"
        return f"{self.full_name} (id:{self.id})"
