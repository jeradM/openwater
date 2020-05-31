import datetime
import logging
import os
from typing import TYPE_CHECKING

from alembic import command
from alembic.config import Config
from databases import Database

from openwater.database.model import (
    zone,
    master_zone_join,
    plugin_config,
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

    try:
        query = zone.insert()
        values = {
            "name": "Master Zone 1",
            "active": True,
            "zone_type": "SHIFT_REGISTER",
            "attrs": {"sr_idx": 0},
        }
        result = await conn.execute(query=query, values=values)
        print("Result: {}".format(result))

        query = zone.insert()
        values = {
            "name": "Test Zone 1",
            "active": True,
            "zone_type": "SHIFT_REGISTER",
            "attrs": {"sr_idx": 1, "soil_type": "CLAY", "precip_rate": 0.2},
        }
        result = await conn.execute(query=query, values=values)
        print("Result: {}".format(result))

        query = master_zone_join.insert()
        values = {"zone_id": 1, "master_zone_id": 0}
        await conn.execute(query=query, values=values)

        query = plugin_config.insert()
        values = {
            "plugin_id": "shift_register",
            "version": 1,
            "config": {
                "num_reg": 8,
                "data_pin": 27,
                "clock_pin": 22,
                "latch_pin": 17,
                "oe_pin": 5,
            },
        }
        await conn.execute(query=query, values=values)
    except Exception:
        await tx.rollback()
    else:
        await tx.commit()


class OWDatabase:
    def __init__(self, ow):
        self.ow = ow
        self._database = Database(ow.config.get("db_url"))

    async def connect(self):
        await self._database.connect()
        self.ow.bus.async_fire("DB_CONNECTED")

    async def disconnect(self):
        await self._database.disconnect()
        self.ow.bus.async_fire("DB_DISCONNECTED")

    def get_session(self):
        pass

    @property
    def connection(self) -> Database:
        return self._database
