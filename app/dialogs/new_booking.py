import datetime as dt
import math
from typing import Any

from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Back, Cancel, Group, Select
from aiogram_dialog.widgets.text import Const, Format, List
from loguru import logger

from app.database import Database
from app.database.models import Place, User
from app.strings import (
    BACK_TEXT,
    ERROR_TEXT,
    INEXISTING_PLACE_TEXT,
    LESS_THAN_MINIMAL_INTERVAL_TIME_TEXT,
    NEW_BOOKING_AVAILABLE_INTERVALS_TEXT,
    NEW_BOOKING_CHOOSE_DAY_TEXT,
    NEW_BOOKING_CHOOSE_PLACE_TEXT,
    NEW_BOOKING_INTERVAL_HELP_TEXT,
    NEW_BOOKING_MINIMAL_INTERVAL_TEXT,
    NEW_BOOKING_NO_INTERVALS_LEFT_TEXT,
    NEW_BOOKING_NO_PLACES_AVAILABLE_TEXT,
    NEW_BOOKING_QUOTA_TEXT,
    NEW_BOOKING_RESULT_TEXT,
    NONWORKING_INTERVAL_TIME_TEXT,
    OCCUPIED_INTERVAL_TIME_TEXT,
    PAST_INTERVAL_TIME_TEXT,
    QUOTA_VIOLATING_INTERVAL_TIME_TEXT,
)
from app.utils.datetime import (
    TimeInterval,
    check_interval_intersections,
    deserialize_date,
    generate_week_items,
    get_free_intervals,
    parse_time_interval,
    serialize_date,
)
from app.utils.layout_widget import Layout


class NewBookingFSM(StatesGroup):
    choosing_place = State()
    choosing_day = State()
    choosing_interval = State()


async def on_place_selected(callback: CallbackQuery, select: Any, manager: DialogManager, item_id: str) -> None:  # noqa: ARG001, ANN401
    manager.dialog_data["place"] = item_id  # type: ignore  # noqa: PGH003
    await manager.switch_to(NewBookingFSM.choosing_day)


async def available_places_getter(db: Database, **_: dict[str, Any]) -> dict[str, list[Place]]:
    places = await db.place.get_all()
    places.sort(key=lambda x: x.id)
    return {"places": places}


choose_place_window = Window(
    Const(NEW_BOOKING_CHOOSE_PLACE_TEXT, when=F["places"].len() > 0),
    Const(NEW_BOOKING_NO_PLACES_AVAILABLE_TEXT, when=F["places"].len() == 0),
    Group(
        Select(
            Format("{item.id}"),
            items="places",
            item_id_getter=lambda x: x.id,
            id="s_places",
            on_click=on_place_selected,
        ),
        width=3,
    ),
    Cancel(Const(BACK_TEXT)),
    state=NewBookingFSM.choosing_place,
    getter=available_places_getter,
)


####


async def on_day_selected(callback: CallbackQuery, select: Any, manager: DialogManager, item_id: str) -> None:  # noqa: ARG001, ANN401
    manager.dialog_data["day"] = item_id  # type: ignore  # noqa: PGH003
    await manager.switch_to(NewBookingFSM.choosing_interval)


async def week_items_getter(**_: dict[str, Any]) -> dict[str, list[tuple[str, dt.datetime]]]:
    return {"week_items": generate_week_items()}


def back_predicate(data: dict[str, Any], widget: Any, dialog_manager: DialogManager) -> bool:  # noqa: ARG001, ANN401
    return not dialog_manager.dialog_data.get("place_selection_skipped", False)  # type: ignore  # noqa: PGH003


def cancel_predicate(data: dict[str, Any], widget: Any, dialog_manager: DialogManager) -> bool:  # noqa: ARG001, ANN401
    return dialog_manager.dialog_data.get("place_selection_skipped", False)  # type: ignore  # noqa: PGH003


choose_day_window = Window(
    Const(NEW_BOOKING_CHOOSE_DAY_TEXT),
    Layout(
        Select(
            Format("{item[0]}"),
            items="week_items",
            item_id_getter=lambda x: serialize_date(x[1]),
            id="s_days",
            on_click=on_day_selected,
        ),
        layout=(1, 3, 3),
    ),
    Back(Const(BACK_TEXT), when=back_predicate),
    Cancel(Const(BACK_TEXT), when=cancel_predicate),
    state=NewBookingFSM.choosing_day,
    getter=week_items_getter,
)


####


async def date_place_getter(dialog_manager: DialogManager, **_: dict[str, Any]) -> dict[str, str]:
    return {
        "date": deserialize_date(dialog_manager.dialog_data["day"]).strftime("%d.%m"),  # type: ignore  # noqa: PGH003
        "place": dialog_manager.dialog_data["place"],  # type: ignore  # noqa: PGH003
    }


async def place_info_getter(
    dialog_manager: DialogManager, db: Database, **_: dict[str, Any]
) -> dict[str, str | int | float | None]:
    date: dt.datetime = deserialize_date(dialog_manager.dialog_data["day"])  # type: ignore  # noqa: PGH003
    place: str = dialog_manager.dialog_data["place"]  # type: ignore  # noqa: PGH003
    user: User = dialog_manager.middleware_data["user_data"]  # type: ignore  # noqa: PGH003
    assert isinstance(user, User)  # noqa: S101
    assert isinstance(place, str)  # noqa: S101
    assert isinstance(date, dt.datetime)  # noqa: S101

    place_object = await db.place.get(place)
    if place_object is None:
        logger.warning(f"Unexisting place {place}")
        return {}

    place_info: dict[str, str | int | float | None] = {
        "place_comment": place_object.comment,
        "minimal_interval": place_object.minimal_interval_minutes,
        "place_quota": place_object.daily_quota_minutes,
    }

    if place_object.daily_quota_minutes is not None:
        existing_bookings = await db.booking.get_by_location(place, date)
        user_time = sum([x.duration for x in filter(lambda b: b.user_id == user.id, existing_bookings)])
        place_info["left_quota"] = math.floor(place_object.daily_quota_minutes - user_time / 60)

    return place_info


async def available_intervals_getter(
    dialog_manager: DialogManager, db: Database, **_: dict[str, Any]
) -> dict[str, list[TimeInterval]]:
    serialized_day: str = dialog_manager.dialog_data["day"]  # type: ignore  # noqa: PGH003
    place: str = dialog_manager.dialog_data["place"]  # type: ignore  # noqa: PGH003
    assert isinstance(serialized_day, str)  # noqa: S101
    assert isinstance(place, str)  # noqa: S101

    day = deserialize_date(serialized_day)
    bookings = await db.booking.get_by_location(place, day)

    place_object = await db.place.get(place)
    if place_object is None:
        logger.warning(f"Unexisting place {place}")
        return {"free_intervals": []}

    free_intervals = get_free_intervals(
        TimeInterval(
            max(place_object.opening_datetime(day), dt.datetime.now(tz=day.tzinfo)), place_object.closing_datetime(day)
        ),
        [TimeInterval(x.start, x.end) for x in bookings],
    )

    free_intervals = list(filter(lambda x: x.duration >= place_object.minimal_interval_minutes * 60, free_intervals))

    return {
        "free_intervals": [
            TimeInterval(x.start.astimezone(day.tzinfo), x.end.astimezone(day.tzinfo)) for x in free_intervals
        ]
    }


async def on_choose_interval_success(
    message: Message,
    widget: Any,  # noqa: ARG001, ANN401
    manager: DialogManager,
    parsed_data: TimeInterval,
) -> None:
    # затыкаем тайпчекер (в aiogram_dialog есть Unknown типы из-за которых линтер превращает код в гирлянду)
    serialized_day: str = manager.dialog_data["day"]  # type: ignore  # noqa: PGH003
    place_id: str = manager.dialog_data["place"]  # type: ignore  # noqa: PGH003
    user: User = manager.middleware_data["user_data"]  # type: ignore  # noqa: PGH003
    db: Database = manager.middleware_data["db"]  # type: ignore  # noqa: PGH003
    assert isinstance(serialized_day, str)  # noqa: S101
    assert isinstance(place_id, str)  # noqa: S101
    assert isinstance(user, User)  # noqa: S101
    assert isinstance(db, Database)  # noqa: S101

    place = await db.place.get(place_id)
    if place is None:
        logger.warning(f"Unexisting place {place_id}")
        await message.answer(ERROR_TEXT.format(error=INEXISTING_PLACE_TEXT))
        await manager.done()
        return

    day = deserialize_date(serialized_day)
    start_time = parsed_data.start.time()
    end_time = parsed_data.end.time()

    end_midnight = end_time == dt.time.fromisoformat("00:00")
    start = dt.datetime.combine(day.date(), start_time, day.tzinfo)
    end = dt.datetime.combine(
        day.date() + (dt.timedelta(days=1) if end_midnight else dt.timedelta()), end_time, day.tzinfo
    )

    # отступ на случай задержки в получении сообщения
    cur_time = (dt.datetime.now(tz=day.tzinfo) - dt.timedelta(minutes=1)).replace(second=0, microsecond=0)
    if start < cur_time:
        logger.info(f"Past-booking attempted at {place_id}, from {start_time} to {end_time}")
        await message.answer(ERROR_TEXT.format(error=PAST_INTERVAL_TIME_TEXT))
        return

    booking_time = (end - start).total_seconds()
    if booking_time / 60 < place.minimal_interval_minutes:
        logger.debug(f"Less than minimal interval for {place_id}, from {start_time} to {end_time}")
        await message.answer(ERROR_TEXT.format(error=LESS_THAN_MINIMAL_INTERVAL_TIME_TEXT))
        return

    if start < place.opening_datetime(day) or end > place.closing_datetime(day):
        logger.debug(f"Error in range check for {place_id}, from {start_time} to {end_time}")
        await message.answer(ERROR_TEXT.format(error=NONWORKING_INTERVAL_TIME_TEXT))
        return

    existing_bookings = await db.booking.get_by_location(place_id, day)

    user_time = sum([x.duration for x in filter(lambda b: b.user_id == user.id, existing_bookings)])
    if place.daily_quota_minutes is not None and ((booking_time + user_time) / 60) > place.daily_quota_minutes:
        logger.info(f"Quota violation attempt by {user.id} by booking from {start_time} to {end_time}")
        await message.answer(ERROR_TEXT.format(error=QUOTA_VIOLATING_INTERVAL_TIME_TEXT))
        return

    if check_interval_intersections(start, end, [TimeInterval(x.start, x.end) for x in existing_bookings]) is True:
        logger.info(f"Error in check intersection (user: {user}) - from {start} to {end}")
        await message.answer(ERROR_TEXT.format(error=OCCUPIED_INTERVAL_TIME_TEXT))
        return

    booking = await db.booking.create({"start": start, "end": end, "user_id": user.id, "place_id": place_id})
    logger.info(f"New booking created: {booking}")

    await message.answer(
        NEW_BOOKING_RESULT_TEXT.format(
            place=place_id,
            date=day.strftime("%d.%m"),
            start_time=start.strftime("%H:%M"),
            end_time=end.strftime("%H:%M"),
        )
    )
    await manager.done()


async def on_choose_interval_error(message: Message, widget: Any, manager: DialogManager, error: ValueError) -> None:  # noqa: ARG001, ANN401
    logger.info(f"Error in day confirmation (user: {manager.middleware_data['user_data']}) {error}")  # type: ignore  # noqa: PGH003
    await message.answer(ERROR_TEXT.format(error=error))


def choosable_interval_predicate(data: dict[str, Any], widget: Any, dialog_manager: DialogManager) -> bool:  # noqa: ARG001, ANN401
    if len(data.get("free_intervals", [])) == 0:
        return False

    if data.get("place_quota") is not None:
        left_quota = data.get("left_quota", 0)
        if left_quota <= 0:
            return False

        minimal_interval = data.get("minimal_interval", 0)
        if minimal_interval > left_quota:
            return False

    return True


choose_interval_window = Window(
    Format(NEW_BOOKING_AVAILABLE_INTERVALS_TEXT, when=F["free_intervals"].len() > 0),
    Format(NEW_BOOKING_NO_INTERVALS_LEFT_TEXT, when=F["free_intervals"].len() == 0),
    List(
        Format("— {item.start.hour:02d}:{item.start.minute:02d} - {item.end.hour:02d}:{item.end.minute:02d}"),
        items="free_intervals",
    ),
    Format(NEW_BOOKING_MINIMAL_INTERVAL_TEXT, when=F["free_intervals"].len() > 0 and F["minimal_interval"] > 0),
    Format(NEW_BOOKING_QUOTA_TEXT, when=F["free_intervals"].len() > 0 and F["place_quota"]),
    Format("{place_comment}", when=F["free_intervals"].len() > 0 and F["place_comment"].len() > 0),
    Const("\n" + NEW_BOOKING_INTERVAL_HELP_TEXT, when=choosable_interval_predicate),
    TextInput(
        id="interval",
        type_factory=parse_time_interval,
        on_success=on_choose_interval_success,
        on_error=on_choose_interval_error,
    ),
    Back(Const(BACK_TEXT)),
    state=NewBookingFSM.choosing_interval,
    getter=[date_place_getter, place_info_getter, available_intervals_getter],
)

####


async def try_skip_place_selection(_: Any, manager: DialogManager) -> None:  # noqa: ANN401
    db: Database = manager.middleware_data["db"]  # type: ignore  # noqa: PGH003
    assert isinstance(db, Database)  # noqa: S101

    places = await db.place.get_all()
    if len(places) == 1:
        manager.dialog_data["place"] = places[0].id  # type: ignore  # noqa: PGH003
        manager.dialog_data["place_selection_skipped"] = True  # type: ignore  # noqa: PGH003
        await manager.switch_to(NewBookingFSM.choosing_day)


new_booking_dialog = Dialog(
    choose_place_window, choose_day_window, choose_interval_window, on_start=try_skip_place_selection
)
