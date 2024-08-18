import datetime as dt

from .base import CRUDBase
from app.database.models import Booking


class CRUDBooking(CRUDBase[Booking]):
    async def create(self, data: dict[str, dt.datetime | int | str]) -> Booking:
        if ("user_id" not in data) or ("place_id" not in data) or ("start" not in data) or ("end" not in data):
            msg = "not enough data to create booking"
            raise ValueError(msg)

        db_obj = self.model(**data)
        self.sess.add(db_obj)
        await self.sess.commit()

        await self.sess.refresh(db_obj)
        return db_obj
