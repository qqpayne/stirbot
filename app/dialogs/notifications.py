from typing import Any

from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Back, Cancel, Row, Select, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, Multi
from loguru import logger

from app.database import Database
from app.database.models import User
from app.strings import (
    BACK_TEXT,
    EXIT_TEXT,
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


class NotificationFSM(StatesGroup):
    main = State()
    configure = State()


async def on_exit(callback: CallbackQuery, _: Any, __: DialogManager) -> None:  # noqa: ANN401
    if isinstance(callback.message, Message):
        await callback.message.delete()


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
    manager.dialog_data["configure_action"] = switchto.widget_id  # type: ignore  # noqa: PGH003


async def update_user_notifs(manager: DialogManager, minutes_before: int | None) -> None:
    db: Database = manager.middleware_data["db"]  # type: ignore  # noqa: PGH003
    user: User = manager.middleware_data["user_data"]  # type: ignore  # noqa: PGH003
    assert isinstance(db, Database)  # noqa: S101
    assert isinstance(user, User)  # noqa: S101

    action = manager.dialog_data["configure_action"]  # type: ignore  # noqa: PGH003
    if action == "before_start":
        await db.user.update(user.id, {"notify_before_start_mins": minutes_before})
        logger.info(f"Changed before start notification delay to {minutes_before} for {user}")
    elif action == "before_end":
        await db.user.update(user.id, {"notify_before_end_mins": minutes_before})
        logger.info(f"Changed before end notification delay to {minutes_before} for {user}")

    await manager.switch_to(NotificationFSM.main)


async def on_config_option_selected(_: CallbackQuery, __: Any, manager: DialogManager, item_id: str) -> None:  # noqa: ANN401
    await update_user_notifs(manager, int(item_id) if int(item_id) > 0 else None)


async def on_text_option_success(_: Message, __: Any, manager: DialogManager, parsed_data: int) -> None:  # noqa: ANN401
    await update_user_notifs(manager, parsed_data if parsed_data > 0 else None)


async def configure_action_text_getter(dialog_manager: DialogManager, **_: dict[str, Any]) -> dict[str, str]:
    action = dialog_manager.dialog_data["configure_action"]  # type: ignore  # noqa: PGH003
    if action == "before_start":
        return {"configure_action_text": NOTIFICATIONS_CONFIGURE_BEFORE_START_TEXT}
    elif action == "before_end":  # noqa: RET505
        return {"configure_action_text": NOTIFICATIONS_CONFIGURE_BEFORE_END_TEXT}
    return {}


notifications_dialog = Dialog(
    Window(
        Multi(
            Const(NOTIFICATIONS_CURRENT_CONFIG_TEXT),
            Format(NOTIFICATIONS_CURRENT_BEFORE_START_SET_TEXT, when=F["before_start_mins"]),
            Const(NOTIFICATIONS_CURRENT_BEFORE_START_NONE_TEXT, when=F["before_start_mins"].is_(None)),
            Format(NOTIFICATIONS_CURRENT_BEFORE_END_SET_TEXT, when=F["before_end_mins"]),
            Const(NOTIFICATIONS_CURRENT_BEFORE_END_NONE_TEXT, when=F["before_end_mins"].is_(None)),
        ),
        Row(
            SwitchTo(
                Const(NOTIFICATIONS_CONFIGURE_BEFORE_START_SWITCH_TEXT),
                id="before_start",
                state=NotificationFSM.configure,
                on_click=on_configure_clicked,
            ),
            SwitchTo(
                Const(NOTIFICATIONS_CONFIGURE_BEFORE_END_SWITCH_TEXT),
                id="before_end",
                state=NotificationFSM.configure,
                on_click=on_configure_clicked,
            ),
            id="action_row",
        ),
        Cancel(Const(EXIT_TEXT), on_click=on_exit),
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
