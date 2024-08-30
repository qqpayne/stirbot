from typing import TypedDict

from .base import CRUDBase
from app.database.models import Rules


class RulesCreateData(TypedDict):
    title: str
    text: str


class RulesUpdateData(TypedDict, total=False):
    title: str
    text: str


class CRUDRules(CRUDBase[Rules, RulesCreateData, RulesUpdateData]):
    pass
