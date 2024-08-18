import datetime as dt
from typing import TypedDict

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
    pass
