from sqlalchemy.ext.asyncio import AsyncSession

from .booking import CRUDBooking
from .place import CRUDPlace
from .user import CRUDUser
from app.database.models import Booking, Place, User


class CRUD:
    def __init__(self, session: AsyncSession) -> None:
        self.user = CRUDUser(session, User)
        self.booking = CRUDBooking(session, Booking)
        self.place = CRUDPlace(session, Place)


__all__ = ["CRUD"]
