from aiogram.types import User as aiogramUser

from .base import CRUDBase
from app.database.models.user import User


class CRUDUser(CRUDBase[User]):
    async def create(self, data: aiogramUser) -> User:
        db_obj = self.model(**data.model_dump(include=set(User.__table__.columns.keys())))
        self.sess.add(db_obj)
        await self.sess.commit()

        await self.sess.refresh(db_obj)
        return db_obj
