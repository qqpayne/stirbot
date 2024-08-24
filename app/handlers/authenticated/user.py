from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart, MagicData
from aiogram_dialog import DialogManager, ShowMode, StartMode

from app import dialogs
from app.dialogs import setup_user_dialog
from app.strings import HELP_TEXT

router = Router(name="user")
router.message.filter(MagicData(F.user_data.is_approved))
router.callback_query.filter(MagicData(F.user_data.is_approved))

setup_user_dialog(router)


@router.message(CommandStart())
async def start_handler(_: types.Message, dialog_manager: DialogManager) -> None:
    """
    Выводит меню с основными действиями
    """
    await dialog_manager.start(dialogs.UserFSM.main, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND)


@router.message(Command("help"))
async def help_handler(message: types.Message) -> None:
    """
    Печатает список доступных команд.
    """
    await message.answer(HELP_TEXT)
