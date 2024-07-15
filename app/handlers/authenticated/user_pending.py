from aiogram import F, Router, types
from aiogram.filters import MagicData

from app.database import Database
from app.strings import SIGNUP_WAIT_TEXT
from app.utils.admin import get_admin_link

router = Router(name="user_pending")
router.message.filter(MagicData(~F.user_data.is_approved))


@router.message()
async def any_message_handler(message: types.Message, db: Database) -> None:
    """
    Сообщает пользователю, ожидающему подтверждения, контакты администратора в ответ на любые сообщения.
    """
    await message.answer(SIGNUP_WAIT_TEXT.format(admin_link=await get_admin_link(db)))
