import datetime as dt
from typing import Literal

from app.config import settings
from app.strings import (
    EMPTY_INTERVAL_TIME_TEXT,
    FRI_TEXT,
    INCORRECT_INTERVAL_FORMAT_TEXT,
    INCORRECT_INTERVAL_TIME_TEXT,
    MON_TEXT,
    NEGATIVE_INTERVAL_TIME_TEXT,
    SAT_TEXT,
    SUN_TEXT,
    THU_TEXT,
    TODAY_TEXT,
    TUE_TEXT,
    WED_TEXT,
)


# Можно использовать локали и %a в strftime, НО локали усложняют деплой и отличаются от дистрибутива к дистрибутиву
def translate_weekday(weekday: Literal["0", "1", "2", "3", "4", "5", "6"]) -> str:  # noqa: PLR0911
    match weekday:
        case "0":
            return SUN_TEXT
        case "1":
            return MON_TEXT
        case "2":
            return TUE_TEXT
        case "3":
            return WED_TEXT
        case "4":
            return THU_TEXT
        case "5":
            return FRI_TEXT
        case "6":
            return SAT_TEXT


def parse_time_interval(text: str) -> tuple[dt.datetime, dt.datetime]:
    """
    Парсит текст вида "%H:%M - %H:%M" на два datetime'а или возвращает ValueError в случае неудачи
    """
    tformat = "%H:%M"
    start, _, end = text.partition("-")

    if len(end) == 0:
        msg = INCORRECT_INTERVAL_FORMAT_TEXT
        raise ValueError(msg)

    try:
        start_dt = dt.datetime.strptime(start.strip(), tformat)  # noqa: DTZ007
        end_dt = dt.datetime.strptime(end.strip(), tformat)  # noqa: DTZ007
    except Exception as err:
        msg = INCORRECT_INTERVAL_TIME_TEXT
        raise ValueError(msg) from err

    if (end_dt - start_dt).days < 0:
        msg = NEGATIVE_INTERVAL_TIME_TEXT
        raise ValueError(msg)

    if start_dt == end_dt:
        msg = EMPTY_INTERVAL_TIME_TEXT
        raise ValueError(msg)

    return (start_dt, end_dt)


def generate_week_items() -> list[tuple[str, dt.datetime]]:
    """
    Создает массив из 7 пар 'название дня - datetime', начиная с сегодняшнего дня в определенном часовом поясе.
    Для сегодняшнего дня используется название "Сегодня", для остальных генерируется по образцу "20.08 (Вт)"
    """
    today = dt.datetime.now(tz=settings.tz)
    next_six_days = [today + dt.timedelta(days=day) for day in range(1, 7)]

    _day_names = [dt.datetime.strftime(date, "%d.%m") for date in next_six_days]
    weekdays = [translate_weekday(dt.datetime.strftime(date, "%w")) for date in next_six_days]  # type: ignore  # noqa: PGH003
    day_names = [f"{pair[0]} ({pair[1]})" for pair in zip(_day_names, weekdays, strict=True)]

    return [(TODAY_TEXT, today)] + list(zip(day_names, next_six_days, strict=True))


def serialize_date(datetime: dt.datetime) -> str:
    return dt.datetime.strftime(datetime, "%x%z")


def deserialize_date(datetime_str: str) -> dt.datetime:
    return dt.datetime.strptime(datetime_str, "%x%z")
