from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message
from loguru import logger

from app.database import Database
from app.database.models import User


class NotAUserFilter(BaseFilter):
    """
    Пропускает только пользователей, не имеющихся в базе данных.
    """

    async def __call__(self, message: Message, db: Database) -> bool:
        if message.from_user is None:
            return True

        user = await db.user.get(message.from_user.id)
        return user is None


class UserFilter(BaseFilter):
    """
    Пропускает только пользователей, о которых имеется запись в базе данных.
    Добавляет к запросу "user_data" с информацией о пользователей.
    """

    async def __call__(self, message: Message, db: Database) -> bool | dict[str, User]:
        if message.from_user is None:
            logger.debug("Non-user message received")
            return False

        user = await db.user.get(message.from_user.id)
        if user is None:
            logger.debug(
                f"Received message from non-authenticated user {message.from_user.full_name} id={message.from_user.id}"
            )
            return False

        return {"user_data": user}


class CalbackAdminFilter(BaseFilter):
    async def __call__(self, callback: CallbackQuery, db: Database) -> bool:
        user = await db.user.get(callback.from_user.id)
        if user is None:
            logger.error(
                f"Received callback from non-authenticated user {callback.from_user.full_name} id={callback.from_user.id}"  # noqa: E501
            )
            return False

        if not user.is_admin:
            logger.error(
                f"Received callback from non-admin user {callback.from_user.full_name} id={callback.from_user.id}"
            )
            return False

        return True
