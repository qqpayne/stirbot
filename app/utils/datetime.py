import datetime as dt
import locale
import zoneinfo

# Для отображения названий дней недели ("%a") и месяцев ("%b") на русском
locale.setlocale(locale.LC_TIME, "ru_RU.utf8")


def parse_time_interval(text: str) -> tuple[dt.datetime, dt.datetime]:
    """
    Парсит текст вида "%H:%M - %H:%M" на два datetime'а или возвращает ValueError в случае неудачи
    """
    tformat = "%H:%M"
    start, _, end = text.partition("-")

    if len(end) == 0:
        msg = "неправильный формат"
        raise ValueError(msg)

    try:
        start_dt = dt.datetime.strptime(start.strip(), tformat)  # noqa: DTZ007
        end_dt = dt.datetime.strptime(end.strip(), tformat)  # noqa: DTZ007
    except Exception as err:
        msg = "введено некорректное время"
        raise ValueError(msg) from err

    if (end_dt - start_dt).days < 0:
        msg = "отрицательный интервал времени"
        raise ValueError(msg)

    return (start_dt, end_dt)


def generate_week_items() -> list[tuple[str, dt.datetime]]:
    """
    Создает массив из 7 пар 'название дня - datetime', начиная с сегодняшнего дня в определенном часовом поясе.
    Для сегодняшнего дня используется название "Сегодня", для остальных генерируется по образцу "20.08 (Вт)"
    """
    # TODO: задавать таймзону через конфиг
    today = dt.datetime.now(tz=zoneinfo.ZoneInfo("Europe/Moscow"))
    next_six_days = [today + dt.timedelta(days=day) for day in range(1, 7)]
    day_names = [dt.datetime.strftime(date, "%d.%m (%a)") for date in next_six_days]
    return [("Сегодня", today)] + list(zip(day_names, next_six_days, strict=True))
