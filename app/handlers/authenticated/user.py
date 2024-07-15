from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart, MagicData

from app.database import Database
from app.strings import HELP_TEXT, REGISTERED_USER_START_TEXT, REPORT_TEXT, RULES_TEXT
from app.utils.admin import get_admin_link

router = Router(name="user")
router.message.filter(MagicData(F.user_data.is_approved))


@router.message(CommandStart())
async def start_handler(message: types.Message) -> None:
    """
    Приветствует пользователя.
    """
    await message.answer(REGISTERED_USER_START_TEXT)


@router.message(Command("help"))
async def help_handler(message: types.Message) -> None:
    """
    Печатает список доступных команд.
    """
    await message.answer(HELP_TEXT)


@router.message(Command("rules"))
async def rules_handler(message: types.Message) -> None:
    """
    Печатает правила пользования ботом и записи на стирку / комнату отдыха.
    """
    await message.answer(RULES_TEXT)


@router.message(Command("report"))
async def report_handler(message: types.Message, db: Database) -> None:
    """
    Возвращает контакты ответственного, которому можно сообщить о нарушениях.
    """
    await message.answer(REPORT_TEXT.format(admin_link=await get_admin_link(db)))
