from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from .base import Base


class Rules(Base):
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    title: Mapped[str]
    text: Mapped[str]

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        return "rules"

    def __repr__(self) -> str:
        return f"rule {self.title} (id:{self.id})"
