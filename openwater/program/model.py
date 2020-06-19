import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, date, time
from enum import Enum
from typing import Collection, Optional, List, Any

from openwater.errors import ProgramException
from openwater.zone.model import BaseZone

_LOGGER = logging.getLogger(__name__)


class BaseProgram(ABC):
    def __init__(
        self,
        id: int,
        name: str,
        steps: List["ProgramStep"] = [],
        schedules: Collection["ProgramSchedule"] = [],
    ):
        self.id = id
        self.name = name
        self.is_running = False
        self._steps = steps
        self.schedules = schedules

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "program_type": self.program_type(),
            "is_running": self.is_running,
            "steps": [s.id for s in self.steps],
            "schedules": [s.id for s in self.schedules],
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


class ScheduleType(Enum):
    WEEKLY = "Weekly"
    INTERVAL = "Interval"
    SINGLE = "Single"


class ProgramSchedule:
    def __init__(
        self,
        *,
        id: int,
        program_id: int,
        schedule_type: str = "Weekly",
        name: str = None,
        enabled: bool = False,
        at: int = None,  # minutes
        day_interval: int = None,  # re-run every n days
        days_restriction: str = None,  # E (even) or O (odd)
        dow_mask: int = 0,  # B2 - 0000001 S, 0000010 M, 0000100 T, ... 1000000 S
        minute_interval: int = None,  # re-run every n minutes
        on_day: date = None,  # for single run program
        start_day: date = None  # for interval program
    ):
        if schedule_type == "Weekly":
            self.type = ScheduleType.WEEKLY
        elif schedule_type == "Interval":
            self.type = ScheduleType.INTERVAL
        elif self.type == "Single":
            self.type = ScheduleType.SINGLE
        else:
            raise ProgramException("Invalid schedule definition")

        self.id = id
        self.program_id = program_id
        self.name = name
        self.enabled = enabled
        self.at = at
        self.dow_mask = dow_mask
        self.days_restriction = days_restriction
        self.start_day = start_day
        self.day_interval = day_interval
        self.minute_interval = minute_interval
        self.on_day: date = on_day

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "program_id": self.program_id,
            "schedule_type": self.type.value,
            "name": self.name,
            "enabled": self.enabled,
            "at": self.at,
            "day_interval": self.day_interval,
            "days_restriction": self.days_restriction,
            "dow_mask": self.dow_mask,
            "minute_interval": self.minute_interval,
            "on_day": self.on_day,
            "start_day": self.start_day,
        }

    def to_db(self) -> dict:
        return self.to_dict()

    def matches(self, dt: datetime) -> bool:
        if self.type == ScheduleType.WEEKLY:
            return self._match_weekly(dt)
        elif self.type == ScheduleType.INTERVAL:
            return self._match_interval(dt)
        elif self.type == ScheduleType.SINGLE:
            return self._match_single(dt)
        else:
            raise ProgramException("Unknown schedule type: {}".format(self.type))

    def _match_weekly(self, dt: datetime) -> bool:
        wd = dt.weekday()
        dow = (wd + 1) % 7
        dow_matches = (1 << dow) & self.dow_mask != 0

        time_mins = (dt.hour * 60) + dt.minute
        time_matches = time_mins == self.at and dt.second < 5

        even = dt.day % 2 == 0
        if not self.days_restriction:
            restricted = False
        elif self.days_restriction == "E":
            restricted = not even
        else:
            restricted = even

        return dow_matches and time_matches and not restricted

    def _match_interval(self, dt: datetime) -> bool:
        first = datetime.combine(
            self.start_day, time(hour=self.at // 60, minute=self.at % 60)
        )
        diff = dt - first
        if self.day_interval:
            time_mins = (dt.hour * 60) + dt.minute
            time_matches = time_mins == self.at and dt.second < 5
            d = diff.days
            return time_matches and (d % self.day_interval == 0)
        else:
            d_min = (diff.days * 24 * 60) + (diff.seconds // 60)
            d_sec = diff.seconds % 60
            return d_min % self.minute_interval == 0 and d_sec < 5

    def _match_single(self, dt: datetime) -> bool:
        time_mins = (dt.hour * 60) + dt.minute
        time_matches = time_mins == self.at and dt.second < 5

        return dt.day == self.on_day.day and time_matches
