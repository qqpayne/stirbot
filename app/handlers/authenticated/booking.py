from aiogram import F, Router, types
from aiogram.filters import Command, MagicData
from aiogram_dialog import DialogManager, StartMode

from app.keyboards.booking import BookingFSM, booking_dialog, edit_booking_dialog, new_booking_dialog

router = Router(name="booking")
router.message.filter(MagicData(F.user_data.is_approved))
router.include_routers(booking_dialog, new_booking_dialog, edit_booking_dialog)


@router.message(Command("booking"))
async def booking_command_handler(message: types.Message, dialog_manager: DialogManager) -> None:  # noqa: ARG001
    """
    Начинает booking-диалог, отправляя пользователю меню с выбором действия: создание новой записи или просмотр грядущих
    """
    await dialog_manager.start(BookingFSM.choosing_action, mode=StartMode.RESET_STACK)  # type: ignore  # noqa: PGH003
