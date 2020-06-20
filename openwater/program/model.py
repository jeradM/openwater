import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Collection, Optional, List

from openwater.zone.model import BaseZone

_LOGGER = logging.getLogger(__name__)


class BaseProgram(ABC):
    def __init__(
        self, id: int, name: str, steps: Optional[List["ProgramStep"]] = None,
    ):
        self.id = id
        self.name = name
        self.is_running = False
        self._steps = steps if steps else list()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "program_type": self.program_type(),
            "is_running": self.is_running,
            "steps": [s.id for s in self.steps],
            "attrs": {},
        }

    def to_db(self) -> dict:
        return {"id": self.id, "name": self.name, "program_type": self.program_type}

    @property
    def steps(self):
        return sorted(self._steps, key=lambda step: step.order)

    @steps.setter
    def steps(self, steps):
        self._steps = steps

    @staticmethod
    @abstractmethod
    def program_type() -> str:
        pass


class ProgramStep:
    """Defines a step in a program"""

    def __init__(
        self,
        id: int,
        duration: int,
        order: int,
        program_id: int,
        zones: Optional[Collection[BaseZone]] = None,
    ):
        self.id = id
        self.duration = duration
        self.order = order
        self.program_id = program_id
        self.zones = zones
        self.running = False
        self.done = False
        self.started_at: Optional[datetime] = None
        self.run_until: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def to_dict(self):
        return {
            "id": self.id,
            "duration": self.duration,
            "program_id": self.program_id,
            "order": self.order,
            "zones": [z.id for z in self.zones],
        }

    def to_db(self):
        return {
            "id": self.id,
            "duration": self.duration,
            "order": self.order,
            "program_id": self.program_id,
        }

    def start(self) -> None:
        self.running = True
        self.started_at = datetime.now()
        self.run_until = self.started_at + timedelta(seconds=self.duration)
        _LOGGER.debug("Starting step: %s", self.to_dict())

    def end(self) -> None:
        self.running = False
        self.done = True
        self.completed_at = datetime.now()

    def is_complete(self):
        if self.done:
            return True
        now = datetime.now()
        return (self.run_until - now).total_seconds() < 1

    def check_open_master_zones(self):
        res = []
        for mz in self.master_zones:
            if mz.open_offset <= 0 or mz.is_open():
                continue
            if self.time_elapsed >= mz.open_offset:
                res.append(mz.id)
        _LOGGER.debug("Checked master zones to open: %s", res)
        return res

    def check_close_master_zones(self, next_step_zones):
        next_ids = [zone.id for zone in next_step_zones]
        res = []
        for mz in self.master_zones:
            if mz.close_offset >= 0 or not mz.is_open():
                continue
            if self.time_remaining <= abs(mz.close_offset) and mz.id not in next_ids:
                res.append(mz.id)
        _LOGGER.debug("Checked master zones to close: %s", res)
        return res

    @property
    def time_remaining(self):
        t = (self.run_until - datetime.now()).total_seconds()
        _LOGGER.debug("Time remaining in program: %d sec", t)
        return t

    @property
    def time_elapsed(self):
        t = (datetime.now() - self.started_at).total_seconds()
        _LOGGER.debug("Time elapsed in program: %d sec", t)
        return t

    @property
    def master_zones(self) -> List["BaseZone"]:
        if self.zones is None:
            return []
        l = []
        for zone in self.zones:
            if zone.master_zones is None:
                continue
            for master in zone.master_zones:
                l.append(master)
        return l
