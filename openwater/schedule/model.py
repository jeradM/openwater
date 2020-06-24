from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Union, Optional

from openwater.errors import ScheduleException


def to_date(d: Union[str, date]) -> date:
    if isinstance(d, str):
        return datetime.strptime(d, "%Y-%m-%d").date()
    return d


class ScheduleType(Enum):
    WEEKLY = "Weekly"
    INTERVAL = "Interval"
    SINGLE = "Single"


class ProgramSchedule:
    def __init__(
        self,
        *,
        id: int = None,
        program_id: int = None,
        schedule_type: str = "Weekly",
        name: str = None,
        enabled: bool = False,
        at: int = None,  # minutes
        day_interval: int = None,  # re-run every n days
        days_restriction: str = None,  # E (even) or O (odd)
        dow_mask: int = 0,  # B2 - 0000001 S, 0000010 M, 0000100 T, ... 1000000 S
        minute_interval: int = None,  # re-run every n minutes
        on_day: Union[str, date] = None,  # for single run program
        start_day: Union[str, date] = None,  # for interval program
        repeat_every: Optional[int] = None,
        repeat_until: Optional[int] = None,
    ):
        if schedule_type == "Weekly":
            self.type = ScheduleType.WEEKLY
        elif schedule_type == "Interval":
            self.type = ScheduleType.INTERVAL
        elif schedule_type == "Single":
            self.type = ScheduleType.SINGLE
        else:
            raise ScheduleException("Invalid schedule definition")

        self.id = id
        self.program_id = program_id
        self.name = name
        self.enabled = enabled
        self.at = at
        self.dow_mask = dow_mask
        self.days_restriction = days_restriction
        self.day_interval = day_interval
        self.minute_interval = minute_interval
        self.on_day: date = to_date(on_day)
        self.start_day: date = to_date(start_day)
        self.repeat_every = repeat_every
        self.repeat_until = repeat_until

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
            "repeat_every": self.repeat_every,
            "repeat_until": self.repeat_until,
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
            raise ScheduleException("Unknown schedule type: {}".format(self.type))

    def _match_weekly(self, dt: datetime) -> bool:
        wd = dt.weekday()
        dow = (wd + 1) % 7
        dow_matches = (1 << dow) & self.dow_mask != 0

        time_mins = (dt.hour * 60) + dt.minute
        time_matches = time_mins == self.at and dt.second < 5

        if (
            time_matches is False
            and self.repeat_every is not None
            and self.repeat_until is not None
            and self.repeat_until >= time_mins
        ):
            time_matches = self.at + self.repeat_every

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
