import datetime
from typing import TYPE_CHECKING

from sqlalchemy import text
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
    comment: Mapped[str] = mapped_column(server_default="")
    daily_quota_minutes: Mapped[int | None] = mapped_column(nullable=True, default=None)
    minimal_interval_minutes: Mapped[int] = mapped_column(server_default=text("0"))
    bookings: Mapped[list["Booking"]] = relationship(back_populates="place")

    def opening_datetime(self, day: datetime.datetime) -> datetime.datetime:
        return datetime.datetime.combine(day.date(), self.opening_hour, day.tzinfo)

    def closing_datetime(self, day: datetime.datetime) -> datetime.datetime:
        close_midnight = self.closing_hour == datetime.time.fromisoformat("00:00")
        return datetime.datetime.combine(
            day.date() + (datetime.timedelta(days=1) if close_midnight else datetime.timedelta()),
            self.closing_hour,
            day.tzinfo,
        )

    def __repr__(self) -> str:
        return f"{self.id} (from {self.opening_hour} to {self.closing_hour})"
