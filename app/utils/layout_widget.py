from collections.abc import Iterable, Sequence
from itertools import chain
from typing import Any, Optional

from aiogram.types import CallbackQuery
from aiogram_dialog.api.internal import ButtonVariant, RawKeyboard
from aiogram_dialog.api.protocols import DialogManager, DialogProtocol
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.kbd.base import Keyboard


# Всё кроме метода _wrap_kbd совпадает с Group за исключнием переименования width в layout
class Layout(Keyboard):
    def __init__(
        self,
        *buttons: Keyboard,
        id: str | None = None,  # noqa: A002
        layout: Sequence[int] | None = None,
        when: WhenCondition = None,
    ) -> None:
        super().__init__(id=id, when=when)
        self.buttons = buttons
        self.layout = layout

    def find(self, widget_id: str) -> Optional["Layout"]:
        widget = super().find(widget_id)
        if widget:
            return widget  # type: ignore[no-any-return]
        for btn in self.buttons:
            widget = btn.find(widget_id)
            if widget:
                return widget  # type: ignore[no-any-return]
        return None

    async def _render_keyboard(
        self,
        data: dict[Any, Any],
        manager: DialogManager,
    ) -> RawKeyboard:
        kbd: RawKeyboard = []
        for b in self.buttons:
            b_kbd = await b.render_keyboard(data, manager)
            if self.layout is None:
                kbd += b_kbd
            else:
                if not kbd:
                    kbd.append([])
                kbd[0].extend(chain.from_iterable(b_kbd))
        if self.layout and kbd:
            kbd = self._wrap_kbd(kbd[0])
        return kbd

    def _wrap_kbd(
        self,
        kbd: Iterable[ButtonVariant],
    ) -> RawKeyboard:
        if not self.layout:
            return [list(kbd)]

        res: RawKeyboard = []
        row: list[ButtonVariant] = []
        idx = 0
        for b in kbd:
            row.append(b)
            if len(row) >= self.layout[idx]:
                res.append(row)
                row = []
                idx += 1
                if idx >= len(self.layout):  # wrap around layout
                    idx = 0
        if row:
            res.append(row)
        return res

    async def _process_other_callback(
        self,
        callback: CallbackQuery,
        dialog: DialogProtocol,
        manager: DialogManager,
    ) -> bool:
        for b in self.buttons:
            if await b.process_callback(callback, dialog, manager):
                return True
        return False
