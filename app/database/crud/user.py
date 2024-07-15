from aiogram.types import User as aiogramUser
from sqlalchemy import select

from .base import CRUDBase
from app.database.models.user import User


class CRUDUser(CRUDBase[User]):
    async def create(self, data: aiogramUser) -> User:
        db_obj = self.model(**data.model_dump(include=set(User.__table__.columns.keys())))
        self.sess.add(db_obj)
        await self.sess.commit()

        await self.sess.refresh(db_obj)
        return db_obj

    async def get_admins(self) -> list[User]:
        query = select(self.model).where(self.model.is_admin == True)  # noqa: E712
        result = await self.sess.execute(query)
        return list(result.scalars())

    async def get_all_unapproved(self) -> list[User]:
        query = select(self.model).where(self.model.is_approved == False)  # noqa: E712
        result = await self.sess.execute(query)
        return list(result.scalars())

    async def approve(self, id: int) -> User:  # noqa: A002
        user = await self.get(id)
        if user is None:
            msg = "user with given id is absent"
            raise ValueError(msg)

        user.is_approved = True
        await self.sess.commit()
        return user

    async def make_admin(self, id: int) -> User:  # noqa: A002
        user = await self.get(id)
        if user is None:
            msg = "user with given id is absent"
            raise ValueError(msg)

        user.is_admin = True
        await self.sess.commit()
        return user

    async def demote_admin(self, id: int) -> User:  # noqa: A002
        user = await self.get(id)
        if user is None:
            msg = "user with given id is absent"
            raise ValueError(msg)

        user.is_admin = False
        await self.sess.commit()
        return user

    async def update(self, id: int, data: aiogramUser) -> User:  # noqa: A002
        db_obj = self.model(**data.model_dump(include=set(User.__table__.columns.keys())))

        existing = await self.get(id)
        if existing is None:
            msg = "user with given id is absent"
            raise ValueError(msg)

        for field in User.__table__.columns.keys():  # noqa: SIM118
            if field in db_obj.__dict__ and getattr(existing, field) != getattr(db_obj, field):
                setattr(existing, field, db_obj.__dict__[field])

        await self.sess.commit()
        await self.sess.refresh(existing)

        return existing
