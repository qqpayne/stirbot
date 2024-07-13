from sqlalchemy.ext.asyncio import AsyncSession

from .user import CRUDUser
from app.database.models import User


class CRUD:
    def __init__(self, session: AsyncSession) -> None:
        self.user = CRUDUser(session, User)


__all__ = ["CRUD"]
