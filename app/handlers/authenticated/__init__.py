from aiogram import Router

from . import admin, booking, user, user_pending
from app.filters import UserFilter

router = Router(name="authenticated")
router.message.filter(UserFilter())
router.callback_query.filter(UserFilter())
router.include_routers(admin.router, user.router, booking.router, user_pending.router)
