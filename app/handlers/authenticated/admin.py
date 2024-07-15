from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart, MagicData
from loguru import logger

from app.database import Database
from app.filters import CalbackAdminFilter
from app.keyboards.new_user import NewUserAction, NewUserCBF, new_user_kb
from app.strings import (
    ADMIN_HELP_TEXT,
    ADMIN_USER_START_TEXT,
    NEW_USER_ALREADY_APPROVED_TEXT,
    NEW_USER_ALREADY_DENIED_TEXT,
    NEW_USER_APPROVED_TEXT,
    NEW_USER_DENIED_TEXT,
    NEW_USER_ERROR_TEXT,
    NEW_USER_TEXT,
    NO_NEW_USERS_TEXT,
)

router = Router(name="admin")
router.message.filter(MagicData(F.user_data.is_admin))


@router.message(CommandStart())
async def start_handler(message: types.Message) -> None:
    """
    Приветствует администратора.
    """
    await message.answer(ADMIN_USER_START_TEXT)


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
    pending = await db.user.get_all_unapproved()

    if len(pending) == 0:
        await message.answer(NO_NEW_USERS_TEXT)
        return

    for user in pending:
        logger.info(f"Preparing new_users_kb for user with id={user.id}")
        await message.answer(NEW_USER_TEXT.format(user_name=user.clickable_name), reply_markup=new_user_kb(user.id))


@router.callback_query(NewUserCBF.filter(), CalbackAdminFilter())
async def new_users_callback_handler(callback: types.CallbackQuery, callback_data: NewUserCBF, db: Database) -> None:
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
    elif callback_data.action is NewUserAction.deny:
        user = await db.user.remove(callback_data.id)
        logger.info(f"Denied access for {user}")
        await callback.message.edit_text(NEW_USER_DENIED_TEXT.format(user_name=user.clickable_name))
    else:
        logger.error("Strange callback data in new users callback")
        await callback.message.edit_text(NEW_USER_ERROR_TEXT)

    await callback.answer()
    return
