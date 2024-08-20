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
