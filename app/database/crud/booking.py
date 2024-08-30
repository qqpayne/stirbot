import datetime as dt
from typing import TypedDict

from sqlalchemy import select

from .base import CRUDBase
from app.database.models import Booking


class BookingCreateData(TypedDict):
    user_id: int
    place_id: str
    start: dt.datetime
    end: dt.datetime


class BookingUpdateData(TypedDict, total=False):
    start: dt.datetime
    end: dt.datetime


class CRUDBooking(CRUDBase[Booking, BookingCreateData, BookingUpdateData]):
    async def get_by_location(self, place: str, day: dt.datetime) -> list[Booking]:
        query = select(self.model).where(
            (self.model.place_id == place) & (self.model.start.between(day, day + dt.timedelta(days=1)))
        )
        result = await self.sess.execute(query)
        return list(result.scalars())

    async def get_users_upcoming(self, user_id: int, at_time: dt.datetime) -> list[Booking]:
        query = select(self.model).where((self.model.user_id == user_id) & (self.model.start >= at_time))
        result = await self.sess.execute(query)
        return list(result.scalars())

    async def get_users_notfinished(self, user_id: int, by_time: dt.datetime) -> list[Booking]:
        query = select(self.model).where((self.model.user_id == user_id) & (self.model.end >= by_time))
        result = await self.sess.execute(query)
        return list(result.scalars())

    async def get_user_ongoing_in_place(self, user_id: int, place_id: str) -> Booking | None:
        query = select(self.model).where(
            (self.model.user_id == user_id)
            & (self.model.place_id == place_id)
            & (self.model.end >= dt.datetime.now(dt.timezone.utc))
            & (self.model.start <= dt.datetime.now(dt.timezone.utc))
        )
        result = await self.sess.execute(query)
        bookings = list(result.scalars())
        if len(bookings) == 0:
            return None
        return bookings[0]
