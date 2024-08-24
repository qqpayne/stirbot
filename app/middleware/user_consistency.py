import contextlib
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware, types
from aiogram.types import Update

from app.exceptions import ObjectNotFoundError

if TYPE_CHECKING:
    from app.database import Database


class UserConsistencyMiddleware(BaseMiddleware):
    """
    Middleware для поддержания консистентности пользовательской информации в БД с информацией в Телеграмме.

    Так как ссылки по айди пользователя не работают, то необходимо использовать username'ы, которые могут меняться.
    Поэтому нужно поддерживать их консистентность с телеграммом.
    """

    async def __call__(  # type: ignore[override]
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: types.Update,
        data: dict[str, Any],
    ) -> Any:  # noqa: ANN401
        db: Database | None = data.get("db")

        user: types.User | None = None
        if event.message and event.message.from_user:
            user = event.message.from_user
        elif event.callback_query:
            user = event.callback_query.from_user

        if user and db:
            with contextlib.suppress(ObjectNotFoundError):
                await db.user.update(
                    user.id,
                    {"username": user.username, "first_name": user.first_name, "last_name": user.last_name},
                )

        return await handler(event, data)
