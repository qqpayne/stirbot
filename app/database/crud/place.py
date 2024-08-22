import datetime as dt
from typing import TypedDict

from .base import CRUDBase
from app.database.models import Place


class PlaceCreateData(TypedDict):
    id: int
    opening_hour: dt.datetime
    closing_hour: dt.datetime
    comment: str
    daily_quota_minutes: int | None
    minimal_interval_minutes: int


class PlaceUpdateData(TypedDict, total=False):
    opening_hour: dt.datetime
    closing_hour: dt.datetime
    comment: str
    daily_quota_minutes: int | None
    minimal_interval_minutes: int


class CRUDPlace(CRUDBase[Place, PlaceCreateData, PlaceUpdateData]):
    pass
