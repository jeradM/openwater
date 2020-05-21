import argparse

import asyncio
import os
import sys



def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='OpenIrrigation: Free, open, extensible irrigation controller')

    parser.add_argument('-c', '--config-dir', help='Specify non-default configuration directory location')
    parser.add_argument('--create-revision', help='Create new database revision')
    parser.add_argument('--upgrade-db', action='store_true', help='Run database migrations')
    parser.add_argument('--revision', help='Target revision for database upgrade', default='head')

    return parser.parse_args()


async def run(args: argparse.Namespace) -> int:
    from openirrigation.database import generate_revision, migrate_db

    from openirrigation import bootstrap
    oi = await bootstrap.setup_oi()
    if args.upgrade_db:
        oi.add_task(migrate_db, oi, args.revision)
        return 0
    if args.create_revision:
        msg = args.create_revision
        oi.add_task(generate_revision, oi, msg)
        return 0
    exit_code = await bootstrap.setup(oi)
    return exit_code


def main() -> int:
    # sys.path.pop(0)
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    args = get_args()
    exit_code = asyncio.run(run(args))
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
