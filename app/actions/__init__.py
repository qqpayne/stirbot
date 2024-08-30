from .base import Action
from .get_previous_user import GetPreviousUserAction

ACTION_LIST = [GetPreviousUserAction()]

__all__ = ["Action", "ACTION_LIST"]
