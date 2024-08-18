from typing import TypedDict

from sqlalchemy import select

from .base import CRUDBase
from app.database.models.user import User


class UserCreateData(TypedDict):
    id: int
    first_name: str
    last_name: str | None
    username: str | None


class UserUpdateData(TypedDict, total=False):
    first_name: str
    last_name: str | None
    username: str | None


class CRUDUser(CRUDBase[User, UserCreateData, UserUpdateData]):
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
