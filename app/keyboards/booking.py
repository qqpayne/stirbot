import datetime as dt
from typing import Any

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Back, Cancel, Column, Select, Start, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, List

from app.database import Database
from app.strings import (
    BACK_TEXT,
    BOOKING_ACTION_EDIT_TEXT,
    BOOKING_ACTION_NEW_TEXT,
    BOOKING_CHOOSE_ACTION_TEXT,
    EDIT_BOOKING_DELETE_ACTION_TEXT,
    EDIT_BOOKING_DELETE_TEXT,
    EDIT_BOOKING_LIST_TEXT,
    ERROR_TEXT,
    NEW_BOOKING_AVAILABLE_INTERVALS_TEXT,
    NEW_BOOKING_CHOOSE_DAY_TEXT,
    NEW_BOOKING_CHOOSE_PLACE_TEXT,
    NEW_BOOKING_INTERVAL_HELP_TEXT,
    NEW_BOOKING_RESULT_TEXT,
)
from app.utils.datetime import generate_week_items, parse_time_interval
from app.utils.layout_widget import Layout


class BookingFSM(StatesGroup):
    choosing_action = State()


class NewBookingFSM(StatesGroup):
    choosing_place = State()
    choosing_day = State()
    confirming_day = State()


class EditBookingFSM(StatesGroup):
    viewing_booking = State()
    removing_booking = State()


async def get_user_bookings(callback: CallbackQuery, widget: Any, manager: DialogManager) -> None:  # noqa: ARG001, ANN401
    db: Database = manager.middleware_data["db"]  # type: ignore  # noqa: PGH003
    assert isinstance(db, Database)  # noqa: S101, необходимо чтоб заткнуть тайпчекер

    if manager.event.from_user is None:
        msg = "non-user message"
        raise ValueError(msg)

    user = await db.user.get(manager.event.from_user.id)  # type: ignore # noqa: F841, PGH003
    # TODO: получать список записей пользователя из БД

    manager.dialog_data["user_bookings"] = ["2к 15.07 16:00-17:30", "2к 15.07 19:00-19:30"]  # type: ignore  # noqa: PGH003


booking_dialog = Dialog(
    Window(
        Const(BOOKING_CHOOSE_ACTION_TEXT),
        Start(Const(BOOKING_ACTION_NEW_TEXT), id="new", state=NewBookingFSM.choosing_place),
        Start(
            Const(BOOKING_ACTION_EDIT_TEXT),
            id="edit",
            state=EditBookingFSM.viewing_booking,
            on_click=get_user_bookings,
        ),
        state=BookingFSM.choosing_action,
    ),
)


async def on_place_selected(callback: CallbackQuery, select: Any, manager: DialogManager, item_id: str) -> None:  # noqa: ARG001, ANN401
    manager.dialog_data["place"] = item_id  # type: ignore  # noqa: PGH003
    await manager.switch_to(NewBookingFSM.choosing_day)


async def on_day_selected(callback: CallbackQuery, select: Any, manager: DialogManager, item_id: str) -> None:  # noqa: ARG001, ANN401
    manager.dialog_data["day"] = item_id  # type: ignore  # noqa: PGH003
    await manager.switch_to(NewBookingFSM.confirming_day)


async def on_day_confirmation_error(message: Message, widget: Any, manager: DialogManager, error: ValueError) -> None:  # noqa: ARG001, ANN401
    await message.answer(ERROR_TEXT.format(error=error))


async def on_day_confirmation_success(
    message: Message,
    widget: Any,  # noqa: ARG001, ANN401
    manager: DialogManager,
    parsed_data: tuple[dt.datetime, dt.datetime],
) -> None:
    day = dt.datetime.strptime(manager.dialog_data["day"], "%x%z")  # type: ignore  # noqa: PGH003
    start = dt.datetime.combine(day.date(), parsed_data[0].time())
    end = dt.datetime.combine(day.date(), parsed_data[1].time())

    # TODO: валидировать что интервал действительно свободен в БД
    # TODO: создавать запись в БД

    await message.answer(
        NEW_BOOKING_RESULT_TEXT.format(
            place=manager.dialog_data["place"],  # type: ignore  # noqa: PGH003
            date=day.strftime("%d.%m"),
            start_time=start.strftime("%H:%M"),
            end_time=end.strftime("%H:%M"),
        )
    )
    await manager.done()


async def available_intervals_getter(
    dialog_manager: DialogManager,
    db: Database,  # noqa: ARG001
    **_: dict[str, Any],
) -> dict[str, str | list[tuple[str, str]]]:
    day = dt.datetime.strptime(dialog_manager.dialog_data["day"], "%x%z")  # type: ignore  # noqa: PGH003
    return {
        "date": day.strftime("%d.%m"),
        "place": dialog_manager.dialog_data["place"],  # type: ignore  # noqa: PGH003
        "free_intervals": [("11:00", "15:00"), ("17:00", "20:00")],  # TODO: получать на основе данных в БД
    }


new_booking_dialog = Dialog(
    Window(
        Const(NEW_BOOKING_CHOOSE_PLACE_TEXT),
        Select(
            Format("{item}"),
            items=["1к (стир.)", "2к (стир.)", "1137"],  # TODO: получать список из БД
            item_id_getter=lambda x: x,
            id="s_places",
            on_click=on_place_selected,
        ),
        Cancel(Const(BACK_TEXT)),
        state=NewBookingFSM.choosing_place,
    ),
    Window(
        Const(NEW_BOOKING_CHOOSE_DAY_TEXT),
        Layout(
            Select(
                Format("{item[0]}"),
                items=generate_week_items(),
                item_id_getter=lambda x: dt.datetime.strftime(x[1], "%x%z"),
                id="s_days",
                on_click=on_day_selected,
            ),
            layout=(1, 3, 3),
        ),
        Back(Const(BACK_TEXT)),
        state=NewBookingFSM.choosing_day,
    ),
    Window(
        Format(NEW_BOOKING_AVAILABLE_INTERVALS_TEXT),
        List(Format("— {item[0]} - {item[1]}"), items="free_intervals"),
        Const(NEW_BOOKING_INTERVAL_HELP_TEXT),
        TextInput(
            id="interval",
            type_factory=parse_time_interval,
            on_success=on_day_confirmation_success,
            on_error=on_day_confirmation_error,
        ),
        Back(Const(BACK_TEXT)),
        state=NewBookingFSM.confirming_day,
        getter=available_intervals_getter,
    ),
)


async def on_delete_booking_selected(
    callback: CallbackQuery,
    select: Any,  # noqa: ANN401
    manager: DialogManager,
    item_id: str,  # noqa: ARG001
) -> None:
    db: Database = manager.middleware_data["db"]  # type: ignore  # noqa: PGH003
    assert isinstance(db, Database)  # noqa: S101, необходимо чтоб заткнуть тайпчекер
    # TODO: удалить запись item_id из БД

    # обновляем список записей пользователя
    await get_user_bookings(callback, select, manager)
    await manager.switch_to(EditBookingFSM.viewing_booking)


edit_booking_dialog = Dialog(
    Window(
        Const(EDIT_BOOKING_LIST_TEXT),
        Column(
            Select(
                Format("{item}"),
                items="user_bookings",
                item_id_getter=lambda x: x,
                id="s_bookings",
            )
        ),
        SwitchTo(
            Const("❌ " + EDIT_BOOKING_DELETE_ACTION_TEXT), id="del_booking", state=EditBookingFSM.removing_booking
        ),
        Cancel(Const(BACK_TEXT)),
        state=EditBookingFSM.viewing_booking,
    ),
    Window(
        Const(EDIT_BOOKING_DELETE_TEXT),
        Column(
            Select(
                Format("❌ {item}"),
                items="user_bookings",
                item_id_getter=lambda x: x,
                id="s_bookings_del",
                on_click=on_delete_booking_selected,
            )
        ),
        Back(Const(BACK_TEXT)),
        state=EditBookingFSM.removing_booking,
    ),
)
