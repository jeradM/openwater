import asyncio
import sys

from openirrigation.config import ensure_config_file, load_config_file
from openirrigation.core import OpenIrrigation
from openirrigation.database import OiDatabase
from openirrigation.utils import plugin_loader
from openirrigation import database

CORE_PLUGINS = [
    'http',
    'rest_api'
]


async def setup_oi() -> OpenIrrigation:
    oi = OpenIrrigation()
    oi.config = await load_config_file(oi)
    return oi


async def setup(oi: OpenIrrigation) -> int:
    if oi.config is None:
        return 2
    db = OiDatabase(oi)
    await db.connect()
    oi.db = db
    await plugin_loader.get_plugins(oi)
    if not oi.config.get('disable_logging', False):
        await plugin_loader.load_logging_plugin(oi)
    await ensure_config_file(oi)
    await plugin_loader.load_plugins(CORE_PLUGINS, oi)
    return await oi.start()
