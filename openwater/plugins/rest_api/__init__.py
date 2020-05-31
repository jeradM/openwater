from typing import Optional

from .endpoints import init_endpoints


async def setup_plugin(ow: "OpenWater", config: Optional[dict] = {}):
    init_endpoints(ow)
