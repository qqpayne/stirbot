from collections.abc import Sequence
from typing import Any

from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, Column, Group, Select
from aiogram_dialog.widgets.text import Const, Format

from app.actions import ACTION_LIST
from app.actions.base import Action
from app.database import Database
from app.database.models import Place
from app.strings import (
    ACTION_EXECUTION_CONDITION_EMOJI,
    BACK_TEXT,
    CHOOSE_ACTION_TEXT,
    EXECUTION_ACTION_TEXT,
    NEW_BOOKING_CHOOSE_PLACE_TEXT,
    NEW_BOOKING_NO_PLACES_AVAILABLE_TEXT,
    NO_ACTIONS_AVAILABLE_TEXT,
)


class ActionsFSM(StatesGroup):
    main = State()
    choose_action = State()
    action_view = State()


async def on_place_selected(_: CallbackQuery, __: Any, manager: DialogManager, item_id: str) -> None:  # noqa: ANN401
    manager.dialog_data["place"] = item_id
    await manager.switch_to(ActionsFSM.choose_action)


async def available_places_getter(db: Database, **_: dict[str, Any]) -> dict[str, list[Place]]:
    places = await db.place.get_all()
    places_with_actions = list(
        filter(lambda place: any(action.is_place_suitable(place.id) for action in ACTION_LIST), places)
    )
    places_with_actions.sort(key=lambda x: x.id)
    return {"places_with_actions": places_with_actions}


async def action_list_getter(dialog_manager: DialogManager, **_: dict[str, Any]) -> dict[str, Sequence[Action]]:
    selected_place = dialog_manager.dialog_data.get("place")
    if selected_place is None:
        return {"actions": ACTION_LIST}

    assert isinstance(selected_place, str)  # noqa: S101
    suitable_actions = list(filter(lambda action: action.is_place_suitable(selected_place), ACTION_LIST))
    return {"actions": suitable_actions}


async def on_action_selected(_: CallbackQuery, __: Any, manager: DialogManager, item_id: str) -> None:  # noqa: ANN401
    manager.dialog_data["selected_action_id"] = item_id
    await manager.switch_to(ActionsFSM.action_view)


async def action_getter(dialog_manager: DialogManager, **_: dict[str, Any]) -> dict[str, Action | bool | None]:
    selected_action_id = dialog_manager.dialog_data["selected_action_id"]
    try:
        action = [action for action in ACTION_LIST if action.id == selected_action_id][0]
    except IndexError:
        await dialog_manager.switch_to(ActionsFSM.main)
        return {"action": None, "can_execute": False}
    return {"action": action, "can_execute": await action.can_execute(dialog_manager)}


async def on_execute(callback: CallbackQuery, _: Any, dialog_manager: DialogManager) -> None:  # noqa: ANN401
    action_info = await action_getter(dialog_manager)
    if isinstance(action_info["action"], Action):
        await action_info["action"](callback, dialog_manager)
        await dialog_manager.done()
    else:
        await dialog_manager.switch_to(ActionsFSM.choose_action)


actions_dialog = Dialog(
    Window(
        Const(NEW_BOOKING_CHOOSE_PLACE_TEXT, when=F["places_with_actions"].len() > 0),
        Const(NEW_BOOKING_NO_PLACES_AVAILABLE_TEXT, when=F["places_with_actions"].len() == 0),
        Group(
            Select(
                Format("{item.id}"),
                items="places_with_actions",
                item_id_getter=lambda x: x.id,
                id="s_places",
                on_click=on_place_selected,
            ),
            width=3,
        ),
        Cancel(Const(BACK_TEXT)),
        state=ActionsFSM.main,
        getter=available_places_getter,
    ),
    Window(
        Const(NO_ACTIONS_AVAILABLE_TEXT, when=F["actions"].len() == 0),
        Const(CHOOSE_ACTION_TEXT, when=F["actions"].len() > 0),
        Column(
            Select(
                Format("{item.title}"),
                items="actions",
                item_id_getter=lambda x: x.id,
                id="s_actions",
                on_click=on_action_selected,
            ),
        ),
        Back(Const(BACK_TEXT)),
        state=ActionsFSM.choose_action,
        getter=action_list_getter,
    ),
    Window(
        Format("<b>{action.title}</b>\n{action.description}"),
        Format(
            "\n" + ACTION_EXECUTION_CONDITION_EMOJI + " {action.execution_conditions}",
            when=F["can_execute"].is_not(True),
        ),
        Button(Const(EXECUTION_ACTION_TEXT), id="execute_action", when="can_execute", on_click=on_execute),
        Back(Const(BACK_TEXT)),
        state=ActionsFSM.action_view,
        getter=action_getter,
    ),
)
