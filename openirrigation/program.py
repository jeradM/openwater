import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional, Union, List, Iterable, Tuple, Callable

from openirrigation.constants import EVENT_TIMER_TICK_SEC, EVENT_PROGRAM_COMPLETED
from openirrigation.model import BaseZone

if TYPE_CHECKING:
    from openirrigation.core import OpenIrrigation, ZoneManager

_LOGGER = logging.getLogger(__name__)


class BaseStep:
    def __init__(self, duration: int):
        self.duration = duration
        self.done = False
        self.started_at: Optional[datetime] = None
        self.run_until: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def start(self) -> None:
        self.started_at = datetime.now()
        self.run_until = self.started_at + timedelta(seconds=self.duration)

    def end(self) -> None:
        self.done = True
        self.completed_at = datetime.now()

    def is_complete(self):
        now = datetime.now()
        return (self.run_until - now).total_seconds() < 1


class ZoneStep(BaseStep):
    """Defines when and for how long a zone should run and tracks a zone's progress"""
    def __init__(self, zone_id: int, duration: int):
        super().__init__(duration)
        self.zone_id = zone_id


class SoakStep(BaseStep):
    """Defines how long to wait during a soak period"""
    def __init__(self, duration: int):
        super().__init__(duration)


class ProgramStep:
    """Represents an individual, serial step in a program which can have multiple zones"""
    def __init__(self, zones: Iterable[BaseStep]):
        self.zones = zones
        self.done: bool = False
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def start(self) -> None:
        self.started_at = datetime.now()
        for zone in self.zones:
            zone.start()

    def end(self) -> None:
        self.done = True
        self.completed_at = datetime.now()

    def is_soak(self):
        return self.zone_id is None

    def get_zones(self, manager: ZoneManager) -> Optional[Iterable[BaseZone]]:
        if self.zone_id is None:
            return None
        if isinstance(self.zone_id, int):
            zone_ids = (self.zone_id,)
        else:
            zone_ids = self.zone_id
        return tuple(manager.get_zone_by_id(zone_id) for zone_id in zone_ids)


class Program:
    def __init__(self, pid: int, oi: OpenIrrigation, steps: List[ProgramStep]):
        self.pid = pid
        self.oi = oi
        self.steps = steps
        self.current_step: Optional[int] = None
        self.remove_listener: Optional[Callable] = None

    def get_zone_ids(self):
        return (z.zone_id for z in self.steps if z.zone_id is not None)

    async def start(self):
        self.remove_listener = self.oi.bus.listen(EVENT_TIMER_TICK_SEC, self.check_progress)
        await self.oi.zone_manager.open_master_zone()

    async def stop(self):
        if self.remove_listener:
            self.remove_listener()

        await self.oi.zone_manager.close_zones(self.get_zone_ids())

    async def check_progress(self):
        step = self.steps[self.current_step]
        if not step.is_complete():
            return

        step.end()
        _LOGGER.debug('Program step {} finished'.format(self.current_step))
        zones = step.get_zones(self.oi.zone_manager)
        for zone in zones:
            await zone.turn_off()

        await self.next_step()

    async def next_step(self):
        next_step_idx = self.current_step + 1 if self.current_step is not None else 0
        if len(self.steps) <= next_step_idx:
            await self.program_complete()
            return
        next_step = self.steps[next_step_idx]
        self.current_step += 1
        for zone in next_step.get_zones(self.oi.zone_manager):
            await zone.turn_on()
        next_step.start()

    async def program_complete(self):
        self.remove_listener()
        self.oi.bus.fire(EVENT_PROGRAM_COMPLETED, data={'program': self, 'now': datetime.now()})
        self.oi.zone_manager.close_master_zone()
