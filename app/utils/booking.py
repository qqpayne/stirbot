import datetime as dt

from app.database.models import Booking, Place


def merge_bookings(bookings: list[Booking]) -> list[Booking]:
    """
    Объединяет записи, если у них совпадает даты конца и начала. Также сортирует список по дате начала записи.
    """
    if len(bookings) == 0:
        return []

    bookings.sort(key=lambda x: x.start)
    merged = [bookings[0]]

    for booking in bookings[1:]:
        cur_start, cur_end = booking.start, booking.end
        last_start, last_end = merged[-1].start, merged[-1].end

        if cur_start == last_end:
            merged[-1] = Booking(start=last_start, end=cur_end)
        else:
            merged.append(booking)

    return merged


def get_free_intervals(place: Place, day_bookings: list[Booking]) -> list[tuple[dt.time, dt.time]]:
    """
    Возвращает список свободных интервалов на день для записи в place, учитывая уже созданные day_bookings и режим
    работы place.

    Записи в day_bookings должны содержать ТОЛЬКО записи на конкретный день.
    """
    # часы в place неявно даны в таймзоне, указанной в настройках. поэтому везде используем local_... у букинга

    merged_bookings = merge_bookings(day_bookings)
    if len(merged_bookings) == 0:
        return [(place.opening_hour, place.closing_hour)]

    # если место работает до полуночи и последняя запись кончается в 00:00, то даты могут отличаться на один день
    last_booking_ends_midnight = merged_bookings[-1].local_end.time() == dt.time.fromisoformat("00:00")
    if merged_bookings[0].local_start.date() != (
        merged_bookings[-1].local_end.date() - (dt.timedelta(days=1) if last_booking_ends_midnight else dt.timedelta())
    ):
        msg = "day_bookings span multiple days"
        raise ValueError(msg)

    intervals: list[tuple[dt.time, dt.time]] = []

    interval_start = place.opening_hour
    start_idx = 0
    if merged_bookings[0].local_start.time() == place.opening_hour:
        interval_start = merged_bookings[0].local_end.time()
        start_idx = 1

    # свободный интервал - это время между концом одной записи и началом другой
    for idx in range(start_idx, len(merged_bookings)):
        interval_end = merged_bookings[idx].local_start.time()
        intervals.append((interval_start, interval_end))
        interval_start = merged_bookings[idx].local_end.time()

    # если последняя запись кончается до закрытия, то добавляем интервал с конца этой записи до закрытия
    if interval_start != place.closing_hour:
        intervals.append((interval_start, place.closing_hour))

    return intervals


def check_intersections(start: dt.datetime, end: dt.datetime, bookings: list[Booking]) -> bool:
    """
    Возвращает True в случае если интервал от start до end накладываются на существующие записи из bookings.
    """
    if start >= end:
        return True

    bookings.sort(key=lambda x: x.start)

    for booking in bookings:
        if booking.end < start:
            continue
        if booking.start > end:
            break

        # Внутри интервала не должно оказаться начала или конца какого-либо booking'а
        if (start <= booking.start < end) or (start < booking.end <= end):
            return True

    return False
