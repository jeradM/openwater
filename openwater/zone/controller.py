import logging
from typing import TYPE_CHECKING, Collection, Dict

from openwater.constants import EVENT_ZONE_CHANGED
from openwater.zone.model import BaseZone

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


class ZoneController:
    def __init__(self, ow: "OpenWater", store: "ZoneStore"):
        self._ow = ow
        self._store = store
        self.zone_types: Dict[str, Dict] = {}
        self.zones: Dict[int, BaseZone] = {}

    async def open_zone(self, zone_id: int):
        target = self._store.get_zone(zone_id)
        if target is None:
            _LOGGER.error("Requested to open a non-existent zone: {}".format(zone_id))
            return
        await target.open()
        self._ow.bus.fire(EVENT_ZONE_CHANGED, target.to_dict())

    async def close_zone(self, zone_id: int):
        target = self._store.get_zone(zone_id)
        if target is None:
            _LOGGER.error("Requested to close a non-existent zone: {}".format(zone_id))
            return
        await target.close()
        self._ow.bus.fire(EVENT_ZONE_CHANGED, target.to_dict())

    async def close_zones(self, zone_ids: Collection[int]):
        for zone_id in zone_ids:
            await self.close_zone(zone_id)
