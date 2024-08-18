from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, created_at, datetime_tz

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
