import datetime
import logging
import os
from typing import TYPE_CHECKING

from alembic import command
from alembic.config import Config
from databases import Database
from sqlalchemy import select

from openwater.database.data import (
    get_zone_data,
    get_master_data,
    get_master_zone_join_data,
    get_program_data,
    get_program_step_data,
    get_program_action_data,
    get_action_zones_data,
    get_schedules_data,
    get_zone_run_data,
)
from openwater.database.model import (
    zone,
    master_zone_join,
    plugin_config,
    program,
    program_run,
    zone_run,
    program_step,
    program_action,
    program_action_zones,
    schedule,
)

if TYPE_CHECKING:
    from openwater.core import OpenWater

MIGRATION_CONFIG_FILE = "alembic.ini"
SCRIPT_DIR_OPT = "script_location"
DB_URL_OPT = "sqlalchemy.url"

_LOGGER = logging.getLogger(__name__)


def migrate_db(ow, revision="head"):
    _LOGGER.info("Running DB migrations. This might take a while")
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    script_dir = os.path.join(cur_dir, "migrations")
    alembic_conf = Config(os.path.join(cur_dir, MIGRATION_CONFIG_FILE))
    alembic_conf.set_main_option(SCRIPT_DIR_OPT, script_dir)
    alembic_conf.set_main_option(DB_URL_OPT, ow.config.get("db_url"))
    command.upgrade(alembic_conf, revision)
    _LOGGER.info("DB migration complete")


def generate_revision(ow, msg=None, autogenerate=True):
    if msg is None:
        msg = "db_revision_{}".format(datetime.datetime.now())
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    script_dir = os.path.join(cur_dir, "migrations")
    alembic_conf = Config(os.path.join(cur_dir, MIGRATION_CONFIG_FILE))
    alembic_conf.set_main_option(SCRIPT_DIR_OPT, script_dir)
    alembic_conf.set_main_option(DB_URL_OPT, ow.config.get("db_url"))
    command.revision(message=msg, config=alembic_conf, autogenerate=autogenerate)


async def populate_db(ow: "OpenWater"):
    conn = ow.db.connection

    tx = await conn.transaction()

    for t in [
        plugin_config,
        master_zone_join,
        program_action_zones,
        program_action,
        program_step,
        program_run,
        schedule,
        program,
        zone_run,
        zone,
    ]:
        await conn.execute(t.delete())

    try:
        await conn.execute(zone.insert(), get_master_data())
        await conn.execute_many(zone.insert(), get_zone_data())
        await conn.execute_many(zone_run.insert(), get_zone_run_data())
        await conn.execute_many(master_zone_join.insert(), get_master_zone_join_data())
        await conn.execute_many(program.insert(), get_program_data())
        await conn.execute_many(program_step.insert(), get_program_step_data())
        await conn.execute_many(program_action.insert(), get_program_action_data())
        await conn.execute_many(program_action_zones.insert(), get_action_zones_data())
        await conn.execute_many(schedule.insert(), get_schedules_data())

        query = plugin_config.insert()
        values = {
            "plugin_id": "shift_register",
            "version": 1,
            "config": {
                "num_reg": 24,
                "data_pin": 27,
                "clock_pin": 22,
                "latch_pin": 17,
                "oe_pin": 5,
            },
        }
        await conn.execute(query=query, values=values)
    except Exception as e:
        print(e)
        await tx.rollback()
    else:
        await tx.commit()


async def test_db(ow: "OpenWater"):
    conn = ow.db.connection
    query = select([program, program_step, program_action]).select_from(
        program.outerjoin(program_step).outerjoin(program_action)
    )
    print(query)
    rows = await conn.fetch_all(query)
    for row in rows:
        print(row)


class OWDatabase:
    def __init__(self, ow):
        self.ow = ow
        self._database = Database(ow.config.get("db_url"))

    async def connect(self):
        await self._database.connect()
        self.ow.bus.fire("DB_CONNECTED")

    async def disconnect(self):
        await self._database.disconnect()
        self.ow.bus.fire("DB_DISCONNECTED")

    def get_session(self):
        pass

    @property
    def connection(self) -> Database:
        return self._database
