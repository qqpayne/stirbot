from aiogram import Dispatcher
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings

jobstores = {
    "default": RedisJobStore(host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD)
}

executors = {"default": AsyncIOExecutor()}
job_defaults = {"coalesce": True, "max_instances": 3, "misfire_grace_time": 0}

scheduler = AsyncIOScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=settings.tz)


async def on_startup() -> None:
    scheduler.start()


async def on_shutdown() -> None:
    scheduler.shutdown()


def setup(dp: Dispatcher) -> None:
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
