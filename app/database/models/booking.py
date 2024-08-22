from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, created_at, datetime_tz
from app.config import settings

if TYPE_CHECKING:
    from .place import Place
    from .user import User


class Booking(Base):
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    place_id: Mapped[str] = mapped_column(ForeignKey("places.id"))
    start: Mapped[datetime_tz]
    end: Mapped[datetime_tz]
    created_at: Mapped[created_at]

    user: Mapped["User"] = relationship(back_populates="bookings")
    place: Mapped["Place"] = relationship(back_populates="bookings")

    @property
    def local_start(self) -> datetime_tz:
        return self.start.astimezone(settings.tz)

    @property
    def local_end(self) -> datetime_tz:
        return self.end.astimezone(settings.tz)

    @property
    def duration(self) -> float:
        return (self.end - self.start).total_seconds()

    def __repr__(self) -> str:
        return (
            f"{self.place_id} "
            f"from {self.local_start.strftime('%x %H:%M')} till {self.local_end.strftime('%x %H:%M')} "
            f"by {self.user_id} (id:{self.id})"
        )
