from typing import TYPE_CHECKING

from openwater.zone.controller import ZoneController
from openwater.zone.registry import ZoneRegistry
from openwater.zone.store import ZoneStore

if TYPE_CHECKING:
    from openwater.core import OpenWater


class ZoneManager:
    def __init__(self, ow: "OpenWater"):
        self.registry = ZoneRegistry()
        self.store = ZoneStore(ow, self.registry)
        self.controller = ZoneController(ow, self.store)
