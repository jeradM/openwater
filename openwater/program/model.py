from abc import ABC, abstractmethod
from datetime import datetime, timedelta, date, time
from enum import Enum
from typing import Collection, Optional

from openwater.errors import ProgramException


class BaseProgram(ABC):
    def __init__(
        self,
        id: int,
        name: str,
        steps: Collection["ProgramStep"] = None,
        schedules: Collection["ProgramSchedule"] = None,
    ):
        self.id = id
        self.name = name
        self.is_running = False
        self.steps = steps
        self.schedules = schedules

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "is_running": self.is_running,
        }


class ProgramAction(ABC):
    """Defines an action to take during a step in a program"""

    def __init__(self, id: int, duration: int):
        self.id = id
        self.duration = duration
        self.running = False
        self.done = False
        self.started_at: Optional[datetime] = None
        self.run_until: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def start(self) -> None:
        self.running = True
        self.started_at = datetime.now()
        self.run_until = self.started_at + timedelta(seconds=self.duration)

    def end(self) -> None:
        self.running = False
        self.done = True
        self.completed_at = datetime.now()

    def is_complete(self):
        if self.done:
            return True
        now = datetime.now()
        return (self.run_until - now).total_seconds() < 1


class SequentialAction(ProgramAction):
    """Defines when and for how long a zone should run and tracks a zone's progress"""

    ACTION_TYPE = "Sequential"

    def __init__(self, zone_id: int, duration: int):
        super().__init__(duration)
        self.zone_id = zone_id


class ParallelAction(ProgramAction):
    ACTION_TYPE = "Parallel"

    def __init__(self, zone_ids: Collection[int], duration: int):
        super().__init__(duration)
        self.zone_ids = zone_ids


class SoakAction(ProgramAction):
    ACTION_TYPE = "Soak"


class ProgramStep:
    """Represents an individual, serial step in a program which can have multiple zones"""

    def __init__(self, id: int, actions: Collection[ProgramAction]):
        self.id: int = id
        self.actions: Collection[ProgramAction] = actions
        self.done: bool = False
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.running_steps: Optional[Collection[ProgramAction]] = None

    def start(self) -> None:
        self.started_at = datetime.now()
        for step in self.actions:
            step.start()

    def end(self) -> None:
        self.done = True
        self.completed_at = datetime.now()

    @property
    def running(self) -> bool:
        return any(a.running for a in self.actions)

    def is_complete(self) -> bool:
        if self.done:
            return True
        return all(a.is_complete() for a in self.actions)


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
        enabled: bool = False,
        at: int = None,  # minutes
        day_interval: int = None,  # re-run every n days
        days_restriction: str = None,  # E (even) or O (odd)
        dow_mask: int = 0,  # B2 - 0000001 S, 0000010 M, 0000100 T, ... 1000000 S
        minute_interval: int = None,  # re-run every n minutes
        on_day: date = None,  # for single run program
        start_day: date = None  # for interval program
    ):
        if dow_mask:
            self.type = ScheduleType.WEEKLY
        elif start_day:
            self.type = ScheduleType.INTERVAL
        elif on_day:
            self.type = ScheduleType.SINGLE
        else:
            raise ProgramException("Invalid schedule definition")

        self.id = id
        self.program_id = program_id
        self.enabled = enabled
        self.at = at
        self.dow_mask = dow_mask
        self.days_restriction = days_restriction
        self.start_day = start_day
        self.day_interval = day_interval
        self.minute_interval = minute_interval
        self.on_day: date = on_day

    def to_dict(self):
        return {
            "id": self.id,
            "program_id": self.program_id,
            "schedule_type": self.type.value,
            "enabled": self.enabled,
            "at": self.at,
            "day_interval": self.day_interval,
            "days_restriction": self.days_restriction,
            "dow_mask": self.dow_mask,
            "minute_interval": self.minute_interval,
            "on_day": self.on_day,
            "start_day": self.start_day,
        }

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
        dow = (dt.weekday() + 2) % 7
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
