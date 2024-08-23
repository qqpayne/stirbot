import datetime as dt
from typing import Any

from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Back, Cancel, Column, Select, SwitchTo
from aiogram_dialog.widgets.text import Const, Format
from loguru import logger

from app.config import settings
from app.database import Database
from app.database.models import Booking, User
from app.strings import (
    BACK_TEXT,
    DELETE_ANOTHERS_BOOKING_TEXT,
    DELETE_NONEXISTING_BOOKING_TEXT,
    DELETE_PAST_BOOKING_TEXT,
    EDIT_BOOKING_DELETE_ACTION_TEXT,
    EDIT_BOOKING_DELETE_TEXT,
    EDIT_BOOKING_EMPTY_TEXT,
    EDIT_BOOKING_LIST_ITEM_TEXT,
    EDIT_BOOKING_LIST_TEXT,
    ERROR_TEXT,
)
from app.utils.notifications import delete_pair as delete_notifs
from app.utils.scheduler import scheduler


class EditBookingFSM(StatesGroup):
    viewing_booking = State()
    removing_booking = State()


async def user_bookings_getter(dialog_manager: DialogManager, **_: dict[str, Any]) -> dict[str, list[Booking] | bool]:
    user = dialog_manager.middleware_data["user_data"]
    assert isinstance(user, User)  # noqa: S101

    bookings: list[Booking] = await user.awaitable_attrs.bookings
    bookings.sort(key=lambda x: x.local_start)

    actual_booking = list(filter(lambda x: x.local_end >= dt.datetime.now(tz=settings.tz), bookings))
    editable_booking = list(filter(lambda x: x.local_start > dt.datetime.now(tz=settings.tz), bookings))

    return {"user_bookings": actual_booking, "editable_bookings": editable_booking}


async def on_delete_booking_selected(
    callback: CallbackQuery,
    select: Any,  # noqa: ARG001, ANN401
    manager: DialogManager,
    item_id: str,
) -> None:
    db = manager.middleware_data["db"]
    user = manager.middleware_data["user_data"]
    assert isinstance(db, Database)  # noqa: S101
    assert isinstance(user, User)  # noqa: S101

    booking = await db.booking.get(int(item_id))
    if booking is None:
        logger.warning(f"Unexisting booking with id {item_id}")
        await callback.answer(ERROR_TEXT.format(error=DELETE_NONEXISTING_BOOKING_TEXT))

    elif booking.user_id != user.id:
        logger.warning(f"User {user.id} tried to delete another's {booking}")
        await callback.answer(ERROR_TEXT.format(error=DELETE_ANOTHERS_BOOKING_TEXT))

    elif booking.local_start <= dt.datetime.now(tz=settings.tz):
        logger.info(f"User {user.id} tried to delete past or ongoing booking {booking}")
        await callback.answer(ERROR_TEXT.format(error=DELETE_PAST_BOOKING_TEXT))

    else:
        await db.booking.remove(booking.id)
        logger.info(f"Deleted booking {booking}")
        await delete_notifs(scheduler, booking)

    await manager.switch_to(EditBookingFSM.viewing_booking)


edit_booking_dialog = Dialog(
    Window(
        Const(EDIT_BOOKING_LIST_TEXT, when=F["user_bookings"].len() > 0),
        Const(EDIT_BOOKING_EMPTY_TEXT, when=F["user_bookings"].len() == 0),
        Column(
            Select(
                Format(EDIT_BOOKING_LIST_ITEM_TEXT),
                items="user_bookings",
                item_id_getter=lambda x: x.id,
                id="s_bookings",
            )
        ),
        SwitchTo(
            Const("❌ " + EDIT_BOOKING_DELETE_ACTION_TEXT),
            id="del_booking",
            state=EditBookingFSM.removing_booking,
            when=F["editable_bookings"].len() > 0,
        ),
        Cancel(Const(BACK_TEXT)),
        state=EditBookingFSM.viewing_booking,
        getter=user_bookings_getter,
    ),
    Window(
        Const(EDIT_BOOKING_DELETE_TEXT),
        Column(
            Select(
                Format("❌ " + EDIT_BOOKING_LIST_ITEM_TEXT),
                items="editable_bookings",
                item_id_getter=lambda x: x.id,
                id="s_bookings_del",
                on_click=on_delete_booking_selected,
            )
        ),
        Back(Const(BACK_TEXT)),
        state=EditBookingFSM.removing_booking,
        getter=user_bookings_getter,
    ),
)
