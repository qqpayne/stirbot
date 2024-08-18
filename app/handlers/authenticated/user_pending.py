from aiogram import F, Router, types
from aiogram.filters import MagicData
from loguru import logger

from app.database import Database
from app.database.models import User
from app.strings import SIGNUP_WAIT_TEXT, UNAUTH_CALLBACK_TEXT
from app.utils.admin import get_admin_link

router = Router(name="user_pending")
router.message.filter(MagicData(~F.user_data.is_approved))
router.callback_query.filter(MagicData(~F.user_data.is_approved))


@router.message()
async def any_message_handler(message: types.Message, db: Database) -> None:
    """
    Сообщает пользователю, ожидающему подтверждения, контакты администратора в ответ на любые сообщения.
    """
    await message.answer(SIGNUP_WAIT_TEXT.format(admin_link=await get_admin_link(db)))


@router.callback_query()
async def any_callback_handler(callback: types.CallbackQuery, user_data: User, db: Database) -> None:
    """
    Предлагает пользователю заново написать администратору в ответ на коллбэк.
    """
    if not isinstance(callback.message, types.Message):
        logger.error("Strange pending callback without message")
        return

    logger.warning("Received callback from unapproved {user}", user=user_data)
    await callback.message.edit_text(UNAUTH_CALLBACK_TEXT)
    await callback.message.answer(SIGNUP_WAIT_TEXT.format(admin_link=await get_admin_link(db)))
    await callback.answer()
