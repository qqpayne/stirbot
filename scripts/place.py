import argparse  # noqa: INP001
import datetime as dt

import uvloop

from app.config import settings
from app.database import Database, sessionmaker


def valid_date(s: str) -> dt.time:
    try:
        return dt.datetime.strptime(s, "%H:%M").replace(tzinfo=settings.tz).timetz()
    except ValueError as err:
        msg = f"not a valid date: {s!r}"
        raise argparse.ArgumentTypeError(msg) from err


async def main() -> None:
    parser = argparse.ArgumentParser(description="Add (default), update or remove booking places")

    parser.add_argument("name", type=str, help="Place name")
    parser.add_argument("opening_hour", type=valid_date, help="Place opening hour in H:M format")
    parser.add_argument("closing_hour", type=valid_date, help="Place closing hour in H:M format")
    parser.add_argument("--update", action="store_true", default=False, help="Update existing place")
    parser.add_argument("--remove", action="store_true", default=False, help="Remove existing place")
    args = parser.parse_args()

    if args.update and args.remove:
        msg = "Can't update and remove place at the same time"
        raise ValueError(msg)

    closing_midnight = args.closing_hour == dt.time.fromisoformat("00:00")
    if args.opening_hour >= args.closing_hour and not closing_midnight:
        msg = "Opening hour should be less than closing hour"
        raise ValueError(msg)

    async with sessionmaker() as session:
        db = Database(session=session)
        if args.remove:
            place = await db.place.remove(args.name)
            print(f"{place.id} has been deleted")  # noqa: T201
        elif args.update:
            place = await db.place.update(
                args.name, {"opening_hour": args.opening_hour, "closing_hour": args.closing_hour}
            )
            print(f"{place} has been updated")  # noqa: T201
        else:
            place = await db.place.create(
                {"id": args.name, "opening_hour": args.opening_hour, "closing_hour": args.closing_hour}
            )
            print(f"{place} has been created")  # noqa: T201


if __name__ == "__main__":
    uvloop.run(main())
