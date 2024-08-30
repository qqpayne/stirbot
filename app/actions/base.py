from abc import abstractmethod
from typing import Protocol, runtime_checkable

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager


@runtime_checkable
class Action(Protocol):
    @property
    @abstractmethod
    def id(self) -> str: ...

    @property
    @abstractmethod
    def title(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @property
    @abstractmethod
    def execution_conditions(self) -> str: ...

    @abstractmethod
    def is_place_suitable(self, place: str) -> bool: ...

    @abstractmethod
    async def can_execute(self, dialog_manager: DialogManager) -> bool: ...

    @abstractmethod
    async def __call__(self, callback_query: CallbackQuery, dialog_manager: DialogManager) -> None: ...
