import datetime as dt

from .base import CRUDBase
from app.database.models import Place


class CRUDPlace(CRUDBase[Place]):
    async def create(self, data: dict[str, dt.datetime | str]) -> Place:
        if ("opening_hour" not in data) or ("closing_hour" not in data) or ("id" not in data):
            msg = "not enough data to create place"
            raise ValueError(msg)

        db_obj = self.model(**data)
        self.sess.add(db_obj)
        await self.sess.commit()

        await self.sess.refresh(db_obj)
        return db_obj

    async def update(self, id: str, data: dict[str, dt.datetime]) -> Place:  # noqa: A002
        db_obj = self.model(id=id, **data)

        existing = await self.get(id)
        if existing is None:
            msg = "place with given id is absent"
            raise ValueError(msg)

        for field in Place.__table__.columns.keys():  # noqa: SIM118
            if field in db_obj.__dict__ and getattr(existing, field) != getattr(db_obj, field):
                setattr(existing, field, db_obj.__dict__[field])

        await self.sess.commit()
        await self.sess.refresh(existing)

        return existing
