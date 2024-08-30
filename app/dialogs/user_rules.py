from typing import Any

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Back, Cancel, Group, Select
from aiogram_dialog.widgets.text import Const, Format

from app.database import Database
from app.database.models import Rules
from app.strings import BACK_TEXT, RULES_CHOICE_ONE_TEXT


class RulesFSM(StatesGroup):
    main = State()
    show_rules = State()


async def rules_list_getter(db: Database, **_: dict[str, Any]) -> dict[str, list[Rules]]:
    rules = await db.rules.get_all()
    rules.sort(key=lambda x: x.id)
    return {"rules": rules}


async def on_rule_selected(_: CallbackQuery, __: Any, manager: DialogManager, item_id: int) -> None:  # noqa: ANN401
    db = manager.middleware_data["db"]
    assert isinstance(db, Database)  # noqa: S101
    rules = await db.rules.get(item_id)
    if rules is None:
        await manager.switch_to(RulesFSM.main)
        return

    manager.dialog_data["rules_text"] = rules.text
    await manager.switch_to(RulesFSM.show_rules)


async def try_skip_rules_selection(_: Any, manager: DialogManager) -> None:  # noqa: ANN401
    db: Database = manager.middleware_data["db"]
    assert isinstance(db, Database)  # noqa: S101

    rules = await db.rules.get_all()
    if len(rules) == 1:
        manager.dialog_data["rules_text"] = rules[0].text
        manager.dialog_data["rules_selection_skipped"] = True
        await manager.switch_to(RulesFSM.show_rules)


def back_predicate(data: dict[str, Any], widget: Any, dialog_manager: DialogManager) -> bool:  # noqa: ARG001, ANN401
    return not dialog_manager.dialog_data.get("rules_selection_skipped", False)


def cancel_predicate(data: dict[str, Any], widget: Any, dialog_manager: DialogManager) -> bool:  # noqa: ARG001, ANN401
    return dialog_manager.dialog_data.get("rules_selection_skipped", False)  # type: ignore[no-any-return]


rules_dialog = Dialog(
    Window(
        Const(RULES_CHOICE_ONE_TEXT),
        Group(
            Select(
                Format("{item.title}"),
                items="rules",
                type_factory=int,
                item_id_getter=lambda x: x.id,
                id="s_rules",
                on_click=on_rule_selected,
            ),
            width=2,
        ),
        Cancel(Const(BACK_TEXT)),
        state=RulesFSM.main,
        getter=rules_list_getter,
    ),
    Window(
        Format("{dialog_data[rules_text]}"),
        Back(Const(BACK_TEXT), when=back_predicate),
        Cancel(Const(BACK_TEXT), when=cancel_predicate),
        state=RulesFSM.show_rules,
    ),
    on_start=try_skip_rules_selection,
)
