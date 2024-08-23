import datetime as dt
from enum import Enum

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from loguru import logger

from app.database.models import Booking
from app.strings import NOTIFICATION_BEFORE_END_TEXT, NOTIFICATION_BEFORE_START_TEXT
from app.utils.scheduler import send_message_job


class ScheduleOn(Enum):
    BEFORE_START = "notify_before_start"
    BEFORE_END = "notify_before_end"


def get_job_prefix(s_type: ScheduleOn, chat_id: int | str, booking_id: int) -> str:
    return f"{s_type.value}:{chat_id}:{booking_id}"


def is_fired_in_past(booking: Booking, schedule_on: ScheduleOn, minutes_before: int) -> bool:
    match schedule_on:
        case ScheduleOn.BEFORE_START:
            target_time = booking.local_start
        case ScheduleOn.BEFORE_END:
            target_time = booking.local_end
    fire_time = target_time - dt.timedelta(minutes=minutes_before)
    return (fire_time - dt.datetime.now(dt.timezone.utc)).total_seconds() < 0


def create(scheduler: AsyncIOScheduler, booking: Booking, schedule_on: ScheduleOn, minutes_before: int) -> None:
    match schedule_on:
        case ScheduleOn.BEFORE_START:
            target_time = booking.local_start
            text_template = NOTIFICATION_BEFORE_START_TEXT
        case ScheduleOn.BEFORE_END:
            target_time = booking.local_end
            text_template = NOTIFICATION_BEFORE_END_TEXT

    chat_id = booking.user_id
    job_id = get_job_prefix(schedule_on, chat_id, booking.id)
    text = text_template.format(place=booking.place_id, time=target_time.strftime("%H:%M"))

    if is_fired_in_past(booking, schedule_on, minutes_before):
        return

    scheduler.add_job(  # type: ignore  # noqa: PGH003
        send_message_job,
        DateTrigger(target_time - dt.timedelta(minutes=minutes_before), target_time.tzinfo),
        id=job_id,
        misfire_grace_time=minutes_before * 60,
        kwargs={"chat_id": chat_id, "message_text": text},
    )
    logger.info(f"Scheduled job {job_id}")


def delete(scheduler: AsyncIOScheduler, booking: Booking, schedule_on: ScheduleOn, minutes_before: int) -> None:
    if is_fired_in_past(booking, schedule_on, minutes_before):
        return
    scheduler.remove_job(get_job_prefix(schedule_on, booking.user_id, booking.id))  # type: ignore  # noqa: PGH003
    # тут логгинг не нужен, APScheduler сам пишет job_id при удалении


async def create_pair(scheduler: AsyncIOScheduler, booking: Booking) -> None:
    user = await booking.awaitable_attrs.user
    if user.notify_before_start_mins is not None:
        create(scheduler, booking, ScheduleOn.BEFORE_START, user.notify_before_start_mins)
    if user.notify_before_end_mins is not None:
        create(scheduler, booking, ScheduleOn.BEFORE_END, user.notify_before_end_mins)


async def delete_pair(scheduler: AsyncIOScheduler, booking: Booking) -> None:
    user = await booking.awaitable_attrs.user
    if user.notify_before_start_mins is not None:
        delete(scheduler, booking, ScheduleOn.BEFORE_START, user.notify_before_start_mins)
    if user.notify_before_end_mins is not None:
        delete(scheduler, booking, ScheduleOn.BEFORE_END, user.notify_before_end_mins)
