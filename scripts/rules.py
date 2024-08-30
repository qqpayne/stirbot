import argparse  # noqa: INP001

import uvloop

from app.database import Database, sessionmaker


async def main() -> None:
    parser = argparse.ArgumentParser(description="Add, update or remove rules")

    parser.add_argument("title", type=str, help="Rules title that will be displayed in selector")
    parser.add_argument("text", type=str, help="Rules text")
    parser.add_argument("--update", type=int, default=-1, help="Update existing rule by id")
    parser.add_argument("--remove", type=int, default=-1, help="Remove existing rule by id")
    args = parser.parse_args()

    if args.update > 0 and args.remove > 0:
        msg = "Can't update and remove rules at the same time"
        raise ValueError(msg)

    async with sessionmaker() as session:
        db = Database(session=session)
        if args.remove > 0:
            rules = await db.rules.remove(args.remove)
            print(f"{rules} has been deleted")  # noqa: T201
        elif args.update > 0:
            rules = await db.rules.update(args.update, {"title": args.title, "text": args.text})
            print(f"{rules} has been updated")  # noqa: T201
        else:
            rules = await db.rules.create({"title": args.title, "text": args.text})
            print(f"{rules} has been created")  # noqa: T201


if __name__ == "__main__":
    uvloop.run(main())
