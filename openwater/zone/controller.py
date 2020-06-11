import logging
from typing import TYPE_CHECKING, Dict

from openwater.constants import EVENT_ZONE_STATE
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

    async def open_zone(self, zone_id: int, open_master: bool = True):
        target = self._store.get_zone(zone_id)
        if target is None:
            _LOGGER.error("Requested to open a non-existent zone: %d", zone_id)
            return
        await target.open()
        _LOGGER.debug("Opened zone %d", zone_id)
        self._ow.bus.fire(EVENT_ZONE_STATE, target)

    async def close_zone(self, zone_id: int, close_master: bool = True):
        target = self._store.get_zone(zone_id)
        if target is None:
            _LOGGER.error("Requested to close a non-existent zone: %d", zone_id)
            return
        await target.close()
        _LOGGER.debug("Closed zone %d", zone_id)
        self._ow.bus.fire(EVENT_ZONE_STATE, target)
