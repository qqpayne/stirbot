from sqlalchemy.ext.asyncio import AsyncSession

from .booking import CRUDBooking
from .place import CRUDPlace
from .rules import CRUDRules
from .user import CRUDUser
from app.database.models import Booking, Place, Rules, User


class CRUD:
    def __init__(self, session: AsyncSession) -> None:
        self.user = CRUDUser(session, User)
        self.booking = CRUDBooking(session, Booking)
        self.place = CRUDPlace(session, Place)
        self.rules = CRUDRules(session, Rules)


__all__ = ["CRUD"]
