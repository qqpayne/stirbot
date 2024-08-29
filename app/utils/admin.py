from aiogram import types
from loguru import logger

from app.database import Database
from app.keyboards.new_user import new_user_kb
from app.strings import (
    NEW_USER_TEXT,
    NO_NEW_USERS_TEXT,
)


async def get_admin_link(db: Database) -> str:
    admin_objs = await db.user.get_admins()

    admins_with_username = list(filter(lambda x: x.username, admin_objs))
    if len(admins_with_username) == 0:
        logger.error("No admins with username")
        return ""

    admin = admins_with_username[0]
    if len(admins_with_username) > 1:
        logger.debug(f"More than one admin is assigned, using {admin} as a primary admin")

    if admin.username is None:
        raise ValueError("unreachable")  # noqa: EM101

    return "@" + admin.username


async def list_new_users(message: types.Message, db: Database) -> None:
    """
    Отправляет администратору сообщения с ждущими регистрации аккаунтами с инлайн-кнопками для подтверждения / отмены.
    """
    pending = await db.user.get_all_unapproved()

    if len(pending) == 0:
        await message.answer(NO_NEW_USERS_TEXT)
        return

    for user in pending:
        logger.info(f"Preparing new_users_kb for user with id={user.id}")
        user_info = (
            user.clickable_name + f" ({user.additional_info})"
            if user.additional_info is not None
            else user.clickable_name
        )
        await message.answer(NEW_USER_TEXT.format(user=user_info), reply_markup=new_user_kb(user.id))
