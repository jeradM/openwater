from openwater.config import ensure_config_file, load_config_file
from openwater.core import OpenWater
from openwater.database import OWDatabase
from openwater.ow_http import setup_http
from openwater.utils import plugin
from openwater.zone.helpers import load_zones

CORE_PLUGINS = ["rest_api", "gpio", "shift_register", "websocket"]


async def setup_ow() -> OpenWater:
    ow = OpenWater()

    # Load pre-launch config
    ow.config = await load_config_file(ow)
    if ow.config is None:
        return 2

    # Initialize OpenWater Web Server
    await setup_http(ow)

    # Setup OpenWater Database Connection
    db = OWDatabase(ow)
    await db.connect()
    ow.db = db

    return ow


async def setup(ow: OpenWater) -> int:
    await plugin.get_plugins(ow)
    if not ow.config.get("disable_logging", False):
        await plugin.load_logging_plugin(ow)
    await ensure_config_file(ow)
    await plugin.load_plugins(CORE_PLUGINS, ow)
    await load_zones(ow)
    return await ow.start()
