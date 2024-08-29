from aiogram import types
from loguru import logger

from app.database import Database
from app.database.models import User
from app.exceptions import ObjectAlreadyExistsError


async def register_new_user(db: Database, user: types.User, approve: bool, additional_info: str | None = None) -> User:  # noqa: FBT001
    """
    Добавляет нового пользователя в базу данных.
    В случае, если пользователь с таким id уже есть в базе - возвращает ошибку.
    """
    if await db.user.get(user.id) is not None:
        raise ObjectAlreadyExistsError

    new_user = await db.user.create(
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "notify_before_end_mins": None,
            "notify_before_start_mins": None,
            "is_approved": approve,
            "additional_info": additional_info,
        }
    )
    logger.info("New user registered: {user} (approved: {approve})", user=new_user, approve=approve)
    return new_user
