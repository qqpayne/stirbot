from typing import Any

from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Cancel, Start
from aiogram_dialog.widgets.text import Const

from .edit_booking import EditBookingFSM, edit_booking_dialog
from .new_booking import NewBookingFSM, new_booking_dialog
from app.strings import (
    BOOKING_ACTION_EDIT_TEXT,
    BOOKING_ACTION_NEW_TEXT,
    BOOKING_CHOOSE_ACTION_TEXT,
    EXIT_TEXT,
)


class BookingFSM(StatesGroup):
    main = State()


async def on_exit(callback: CallbackQuery, button: Any, manager: DialogManager) -> None:  # noqa: ARG001, ANN401
    if isinstance(callback.message, Message):
        await callback.message.delete()


booking_dialog = Dialog(
    Window(
        Const(BOOKING_CHOOSE_ACTION_TEXT),
        Start(Const(BOOKING_ACTION_NEW_TEXT), id="new", state=NewBookingFSM.choosing_place),
        Start(Const(BOOKING_ACTION_EDIT_TEXT), id="edit", state=EditBookingFSM.viewing_booking),
        Cancel(Const(EXIT_TEXT), on_click=on_exit),
        state=BookingFSM.main,
    ),
)


def setup_booking_dialog(router: Router) -> None:
    router.include_routers(new_booking_dialog, booking_dialog, edit_booking_dialog)
