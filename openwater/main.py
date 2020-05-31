import argparse

import asyncio
import os
import sys


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="OpenWater: Free, open, extensible irrigation controller"
    )

    parser.add_argument(
        "-c",
        "--config-dir",
        help="Specify non-default configuration directory location",
    )
    parser.add_argument("--create-revision", help="Create new database revision")
    parser.add_argument(
        "--upgrade-db", action="store_true", help="Run database migrations"
    )
    parser.add_argument(
        "--revision", help="Target revision for database upgrade", default="head"
    )
    parser.add_argument(
        "--populate", action="store_true", help="Populate database with test data"
    )
    parser.add_argument(
        "--mock-gpio", action="store_true", help="Mock RPi.GPIO module for development"
    )

    return parser.parse_args()


async def run(args: argparse.Namespace) -> int:
    from openwater.database import generate_revision, migrate_db, populate_db
    from openwater import bootstrap

    ow = await bootstrap.setup_ow()
    if args.upgrade_db:
        ow.async_add_task(migrate_db, ow, args.revision)
        return 0
    if args.create_revision:
        msg = args.create_revision
        ow.async_add_task(generate_revision, ow, msg)
        return 0
    if args.populate:
        await populate_db(ow)
        return 0
    if args.mock_gpio:
        import fake_rpi

        sys.modules["RPi"] = fake_rpi.RPi
        sys.modules["RPi.GPIO"] = fake_rpi.RPi.GPIO
        sys.modules["smbus"] = fake_rpi.smbus
    exit_code = await bootstrap.setup(ow)
    return exit_code


def main() -> int:
    # sys.path.pop(0)
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root_path)
    ow_path = os.path.join(root_path, "openwater")
    while ow_path in sys.path:
        sys.path.remove(ow_path)
    for p in sys.path:
        print(p)
    args = get_args()
    exit_code = asyncio.run(run(args))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
