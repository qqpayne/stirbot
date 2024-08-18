import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import Booking


class Place(Base):
    id: Mapped[str] = mapped_column(primary_key=True, unique=True, autoincrement=False)
    # Время можно хранить с таймзоной, но это не рекомендуется (см. документация PostgreSQL)
    # Лучше использовать знания о таймзоне в самом боте
    opening_hour: Mapped[datetime.time]
    closing_hour: Mapped[datetime.time]
    bookings: Mapped[list["Booking"]] = relationship(back_populates="place")

    def __repr__(self) -> str:
        return f"{self.id} (from {self.opening_hour} to {self.closing_hour})"
