import logging
from typing import Optional


async def setup_plugin(ow: "OpenWater", config: Optional[dict] = {}):
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
