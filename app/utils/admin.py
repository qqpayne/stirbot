from aiogram.types import User as aioUser
from loguru import logger

from app.database import Database
from app.database.models import User


async def get_admin_link(db: Database) -> str:
    admin_objs = await db.user.get_admins()

    admins_with_username = list(filter(lambda x: x.username, admin_objs))
    if len(admins_with_username) == 0:
        logger.error("No admins with username")
        return ""

    admin = admins_with_username[0]
    if len(admins_with_username) > 1:
        logger.debug(f"More than one admin is assigned, using {admin} as a primary admin")

    if admin.username is None:
        raise ValueError("unreachable")  # noqa: EM101

    return "@" + admin.username


# Так как ссылки по айди не работают, то нужно отображать username админов.
# Эта информация может меняться, поэтому нужно иногда её обновлять. Это удобно делать в аутентификационном фильтре.
async def update_admin_info(user: User, db: Database, new_info: aioUser) -> None:
    if user.is_admin:
        logger.debug(f"Updating admin {user} info")
        await db.user.update(
            user.id, {"username": new_info.username, "first_name": new_info.first_name, "last_name": new_info.last_name}
        )
