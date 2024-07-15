import argparse  # noqa: INP001

import uvloop

from app.database import Database, sessionmaker


async def main() -> None:
    parser = argparse.ArgumentParser(description="Make bot user admin or demote him")

    parser.add_argument("uid", type=int)
    parser.add_argument("--demote", action="store_true", default=False, help="remove admin rights from user")
    args = parser.parse_args()

    async with sessionmaker() as session:
        db = Database(session=session)
        if args.demote:
            user = await db.user.demote_admin(args.uid)
            print(f"{user} has lost administrator rights")  # noqa: T201
        else:
            user = await db.user.make_admin(args.uid)
            print(f"{user} is now an admin")  # noqa: T201


if __name__ == "__main__":
    uvloop.run(main())
