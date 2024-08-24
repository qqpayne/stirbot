from aiogram import Bot, F, Router, types
from aiogram.filters import Command, MagicData
from loguru import logger

from app.database import Database
from app.dialogs import setup_admin_dialog
from app.keyboards.new_user import NewUserAction, NewUserCBF
from app.strings import (
    ADMIN_HELP_TEXT,
    NEW_USER_ALREADY_APPROVED_TEXT,
    NEW_USER_ALREADY_DENIED_TEXT,
    NEW_USER_APPROVED_TEXT,
    NEW_USER_DENIED_TEXT,
    NEW_USER_ERROR_TEXT,
    NOTIFY_APPROVED_USER_TEXT,
    NOTIFY_DENIED_USER_TEXT,
)
from app.utils.admin import list_new_users

router = Router(name="admin")
router.message.filter(MagicData(F.user_data.is_admin))
router.callback_query.filter(MagicData(F.user_data.is_admin))

setup_admin_dialog(router)


@router.message(Command("help"))
async def help_handler(message: types.Message) -> None:
    """
    Отправляет администратору список доступных команд, включая доступные только администратору.
    """
    await message.answer(ADMIN_HELP_TEXT)


@router.message(Command("new_users"))
async def new_users_command_handler(message: types.Message, db: Database) -> None:
    """
    Отправляет администратору сообщения с ждущими регистрации аккаунтами с инлайн-кнопками для подтверждения / отмены.
    """
    await list_new_users(message, db)


@router.callback_query(NewUserCBF.filter())
async def new_users_callback_handler(
    callback: types.CallbackQuery, callback_data: NewUserCBF, db: Database, bot: Bot
) -> None:
    if not isinstance(callback.message, types.Message):
        logger.error("Something is not right with new users callback")
        return

    # Валидация на залежавшиеся коллбэки
    user = await db.user.get(callback_data.id)
    if user is None:
        logger.info(f"New users callback called for already deleted user with id={callback_data.id}")
        await callback.message.edit_text(NEW_USER_ALREADY_DENIED_TEXT.format(user_id=callback_data.id))
        await callback.answer()
        return
    if user.is_approved:
        logger.info(f"Callback called for already approved {user}")
        await callback.message.edit_text(NEW_USER_ALREADY_APPROVED_TEXT.format(user_name=user.clickable_name))
        await callback.answer()
        return

    if callback_data.action is NewUserAction.approve:
        user = await db.user.approve(callback_data.id)
        logger.info(f"Approved access for {user}")
        await callback.message.edit_text(NEW_USER_APPROVED_TEXT.format(user_name=user.clickable_name))
        await bot.send_message(user.id, NOTIFY_APPROVED_USER_TEXT)
    elif callback_data.action is NewUserAction.deny:
        user = await db.user.remove(callback_data.id)
        logger.info(f"Denied access for {user}")
        await callback.message.edit_text(NEW_USER_DENIED_TEXT.format(user_name=user.clickable_name))
        await bot.send_message(user.id, NOTIFY_DENIED_USER_TEXT)
    else:
        logger.error("Strange callback data in new users callback")
        await callback.message.edit_text(NEW_USER_ERROR_TEXT)

    await callback.answer()
    return
