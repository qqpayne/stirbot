from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: type[ModelType]) -> None:
        self.sess = session
        self.model = model

    async def get(self, id: Any) -> ModelType | None:  # noqa: ANN401, A002
        return await self.sess.get(self.model, id)

    async def get_multi(self, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        query = select(self.model).order_by(self.model.id).offset(skip).fetch(limit)
        result = await self.sess.execute(query)
        return list(result.scalars())

    async def get_all(self) -> list[ModelType]:
        query = select(self.model)
        result = await self.sess.execute(query)
        return list(result.scalars())

    async def remove(self, id: Any) -> ModelType:  # noqa: ANN401, A002
        obj = await self.sess.get(self.model, id)
        if obj is None:
            raise ValueError
        await self.sess.delete(obj)
        await self.sess.commit()
        return obj

    async def create(self, data: Any) -> ModelType:  # noqa: ANN401
        raise NotImplementedError

    async def update(self, id: Any, data: Any) -> ModelType:  # noqa: ANN401, A002
        raise NotImplementedError
