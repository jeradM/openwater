import logging
from asyncio import TimerHandle
from typing import TYPE_CHECKING, Dict, Any

from openwater.constants import EVENT_ZONE_STATE
from openwater.zone.model import BaseZone

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


class ZoneController:
    def __init__(self, ow: "OpenWater", store: "ZoneStore"):
        self._ow = ow
        self._store = store
        self.zone_types: Dict[str, Dict] = dict()
        self.zones: Dict[int, BaseZone] = dict()
        self._zone_open_jobs: Dict[int, Dict[int, TimerHandle]] = dict()

    async def open_zone(self, zone_id: int):
        target: "BaseZone" = self._store.get(zone_id)
        if target is None:
            _LOGGER.error("Requested to open a non-existent zone: %d", zone_id)
            return
        for m_id, job in self._zone_open_jobs.get(target.id, {}).values():
            if job and not job.cancelled():
                job.cancel()
                self._zone_open_jobs[target.id].pop(m_id)
        if not target.master_zones:
            await target.open()
        else:
            masters = sorted(
                [mz for mz in target.master_zones if not mz.is_open()],
                key=lambda z: z.open_offset,
                reverse=True,
            )
            master_zero = masters[0]
            for master in masters:
                if self._zone_open_jobs.get(target.id) is None:
                    self._zone_open_jobs[target.id] = dict()
                self._zone_open_jobs[target.id][master.id] = self._ow.run_coroutine_in(
                    master.open(), master_zero.open_offset - master.open_offset
                )
                self._zone_open_jobs[target.id][target.id] = self._ow.run_coroutine_in(
                    target.open(), master_zero.open_offset
                )
        _LOGGER.debug("Opened zone %d", zone_id)

    async def close_zone(self, zone_id: int, close_master: bool = True):
        target = self._store.get(zone_id)
        if target is None:
            _LOGGER.error("Requested to close a non-existent zone: %d", zone_id)
            return
        for m_id, job in self._zone_open_jobs.get(target.id, {}).values():
            if job and not job.cancelled():
                job.cancel()
                self._zone_open_jobs[target.id].pop(m_id)
        await target.close()
        _LOGGER.debug("Closed zone %d", zone_id)
        self._ow.bus.fire(EVENT_ZONE_STATE, target)
