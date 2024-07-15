from aiogram.utils.link import create_tg_link
from loguru import logger

from app.database import Database


# Если будет слишком часто вызываться, то можно добавить кэширование, потому что эти данные почти не меняются
async def get_admin_link(db: Database) -> str:
    admin_objs = await db.user.get_admins()
    admin = admin_objs[0]
    if len(admin_objs) > 1:
        logger.debug("More than one admin is assigned, using '{id}' as a primary admin", id=admin.id)
    return create_tg_link("user", id=admin.id)


async def get_admin_text_link(db: Database, link_text: str) -> str:
    link = await get_admin_link(db)
    return f"<a href='{link}'>{link_text}</a>"
