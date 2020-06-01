from typing import TYPE_CHECKING, Optional

from .endpoints import init_endpoints

if TYPE_CHECKING:
    from openwater.core import OpenWater


async def setup_plugin(ow: "OpenWater", config: Optional[dict] = {}):
    init_endpoints(ow)
