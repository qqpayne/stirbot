import datetime as dt
from enum import Enum
from typing import Any

from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Back, Cancel, Select, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, Multi
from loguru import logger

from app.database import Database
from app.database.models import User
from app.strings import (
    BACK_TEXT,
    MINUTES_TEXT,
    NOTIFICATIONS_CONFIGURE_BEFORE_END_SWITCH_TEXT,
    NOTIFICATIONS_CONFIGURE_BEFORE_END_TEXT,
    NOTIFICATIONS_CONFIGURE_BEFORE_START_SWITCH_TEXT,
    NOTIFICATIONS_CONFIGURE_BEFORE_START_TEXT,
    NOTIFICATIONS_CONFIGURE_TEXT,
    NOTIFICATIONS_CURRENT_BEFORE_END_NONE_TEXT,
    NOTIFICATIONS_CURRENT_BEFORE_END_SET_TEXT,
    NOTIFICATIONS_CURRENT_BEFORE_START_NONE_TEXT,
    NOTIFICATIONS_CURRENT_BEFORE_START_SET_TEXT,
    NOTIFICATIONS_CURRENT_CONFIG_TEXT,
    NOTIFICATIONS_TURNOFF_OPTION_TEXT,
)
from app.utils import notifications as notifs
from app.utils.scheduler import scheduler


class ConfigureAction(Enum):
    BEFORE_START = "before_start"
    BEFORE_END = "before_end"


class NotificationFSM(StatesGroup):
    main = State()
    configure = State()


async def current_config_getter(user_data: User, **_: dict[str, Any]) -> dict[str, int | None]:
    return {
        "before_start_mins": user_data.notify_before_start_mins,
        "before_end_mins": user_data.notify_before_end_mins,
    }


async def on_configure_clicked(
    _: CallbackQuery,
    switchto: Any,  # noqa: ANN401
    manager: DialogManager,
) -> None:
    manager.dialog_data["configure_action"] = switchto.widget_id


async def update_user_notifs(manager: DialogManager, minutes_before: int | None) -> None:
    db: Database = manager.middleware_data["db"]
    user: User = manager.middleware_data["user_data"]
    assert isinstance(db, Database)  # noqa: S101
    assert isinstance(user, User)  # noqa: S101

    action = ConfigureAction(manager.dialog_data["configure_action"])
    match action:
        case ConfigureAction.BEFORE_START:
            previous_min_before = user.notify_before_start_mins
            schedule_on = notifs.ScheduleOn.BEFORE_START
            await db.user.update(user.id, {"notify_before_start_mins": minutes_before})
            logger.info(f"Changed before start notification delay to {minutes_before} for {user}")
            bookings_to_reschedule = await db.booking.get_users_upcoming(user.id, dt.datetime.now(dt.timezone.utc))
        case ConfigureAction.BEFORE_END:
            previous_min_before = user.notify_before_end_mins
            schedule_on = notifs.ScheduleOn.BEFORE_END
            await db.user.update(user.id, {"notify_before_end_mins": minutes_before})
            logger.info(f"Changed before end notification delay to {minutes_before} for {user}")
            bookings_to_reschedule = await db.booking.get_users_notfinished(user.id, dt.datetime.now(dt.timezone.utc))

    if previous_min_before != minutes_before:
        if previous_min_before is not None:
            [notifs.delete(scheduler, booking, schedule_on, previous_min_before) for booking in bookings_to_reschedule]  # type: ignore[func-returns-value]
        if minutes_before is not None:
            [notifs.create(scheduler, booking, schedule_on, minutes_before) for booking in bookings_to_reschedule]  # type: ignore[func-returns-value]

    await manager.switch_to(NotificationFSM.main)


async def on_config_option_selected(_: CallbackQuery, __: Any, manager: DialogManager, item_id: str) -> None:  # noqa: ANN401
    await update_user_notifs(manager, int(item_id) if int(item_id) > 0 else None)


async def on_text_option_success(_: Message, __: Any, manager: DialogManager, parsed_data: int) -> None:  # noqa: ANN401
    await update_user_notifs(manager, parsed_data if parsed_data > 0 else None)


async def configure_action_text_getter(dialog_manager: DialogManager, **_: dict[str, Any]) -> dict[str, str]:
    action = ConfigureAction(dialog_manager.dialog_data["configure_action"])

    match action:
        case ConfigureAction.BEFORE_START:
            return {"configure_action_text": NOTIFICATIONS_CONFIGURE_BEFORE_START_TEXT}
        case ConfigureAction.BEFORE_END:
            return {"configure_action_text": NOTIFICATIONS_CONFIGURE_BEFORE_END_TEXT}


notifications_dialog = Dialog(
    Window(
        Multi(
            Const(NOTIFICATIONS_CURRENT_CONFIG_TEXT),
            Format(NOTIFICATIONS_CURRENT_BEFORE_START_SET_TEXT, when=F["before_start_mins"]),
            Const(NOTIFICATIONS_CURRENT_BEFORE_START_NONE_TEXT, when=F["before_start_mins"].is_(None)),
            Format(NOTIFICATIONS_CURRENT_BEFORE_END_SET_TEXT, when=F["before_end_mins"]),
            Const(NOTIFICATIONS_CURRENT_BEFORE_END_NONE_TEXT, when=F["before_end_mins"].is_(None)),
        ),
        SwitchTo(
            Const(NOTIFICATIONS_CONFIGURE_BEFORE_START_SWITCH_TEXT),
            id=ConfigureAction.BEFORE_START.value,
            state=NotificationFSM.configure,
            on_click=on_configure_clicked,
        ),
        SwitchTo(
            Const(NOTIFICATIONS_CONFIGURE_BEFORE_END_SWITCH_TEXT),
            id=ConfigureAction.BEFORE_END.value,
            state=NotificationFSM.configure,
            on_click=on_configure_clicked,
        ),
        Cancel(Const(BACK_TEXT)),
        state=NotificationFSM.main,
        getter=current_config_getter,
    ),
    Window(
        Format(NOTIFICATIONS_CONFIGURE_TEXT),
        Select(
            Format("{item[0]}"),
            items=[(NOTIFICATIONS_TURNOFF_OPTION_TEXT, -1), ("5 " + MINUTES_TEXT, 5), ("15 " + MINUTES_TEXT, 15)],
            item_id_getter=lambda x: x[1],
            id="s_configure_options",
            on_click=on_config_option_selected,
        ),
        TextInput(id="i_minutes", type_factory=int, on_success=on_text_option_success),
        Back(Const(BACK_TEXT)),
        state=NotificationFSM.configure,
        getter=configure_action_text_getter,
    ),
)


def setup_notifications_dialog(router: Router) -> None:
    router.include_routers(notifications_dialog)
