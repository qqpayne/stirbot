from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Cancel, Start
from aiogram_dialog.widgets.text import Const

from .edit_booking import EditBookingFSM, edit_booking_dialog
from .new_booking import NewBookingFSM, new_booking_dialog
from app.strings import (
    BACK_TEXT,
    BOOKING_ACTION_EDIT_TEXT,
    BOOKING_ACTION_NEW_TEXT,
    BOOKING_CHOOSE_ACTION_TEXT,
)


class BookingFSM(StatesGroup):
    main = State()


booking_dialog = Dialog(
    Window(
        Const(BOOKING_CHOOSE_ACTION_TEXT),
        Start(Const(BOOKING_ACTION_NEW_TEXT), id="new", state=NewBookingFSM.choosing_place),
        Start(Const(BOOKING_ACTION_EDIT_TEXT), id="edit", state=EditBookingFSM.viewing_booking),
        Cancel(Const(BACK_TEXT)),
        state=BookingFSM.main,
    ),
)


def setup_booking_dialog(router: Router) -> None:
    router.include_routers(new_booking_dialog, booking_dialog, edit_booking_dialog)
