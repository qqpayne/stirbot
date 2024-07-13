import datetime
from typing import Annotated, Any

from sqlalchemy import BigInteger, text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr, mapped_column

int_pk = Annotated[int, mapped_column(primary_key=True, unique=True, autoincrement=False)]
big_int_pk = Annotated[int, mapped_column(primary_key=True, unique=True, autoincrement=False, type_=BigInteger)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    id: Any

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        return f"{cls.__name__.lower()}s"
