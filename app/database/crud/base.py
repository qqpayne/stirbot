from collections.abc import Mapping
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Base
from app.exceptions import ObjectNotFoundError

ModelType = TypeVar("ModelType", bound=Base)
CreateDataType = TypeVar("CreateDataType", bound=Mapping[str, Any])
UpdateDataType = TypeVar("UpdateDataType", bound=Mapping[str, Any])


class CRUDBase(Generic[ModelType, CreateDataType, UpdateDataType]):
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
            raise ObjectNotFoundError
        await self.sess.delete(obj)
        await self.sess.commit()
        return obj

    async def create(self, data: CreateDataType) -> ModelType:
        db_obj = self.model(**data)
        self.sess.add(db_obj)
        await self.sess.commit()

        await self.sess.refresh(db_obj)
        return db_obj

    async def update(self, id: Any, data: UpdateDataType) -> ModelType:  # noqa: ANN401, A002
        existing = await self.get(id)
        if existing is None:
            raise ObjectNotFoundError

        for field in self.model.__table__.columns.keys():  # noqa: SIM118
            if field in data and getattr(existing, field) != data[field]:
                setattr(existing, field, data[field])

        await self.sess.commit()
        await self.sess.refresh(existing)

        return existing
