from typing import TYPE_CHECKING, List, Optional

from cerberus.errors import ErrorList

from openwater.constants import EVENT_SCHEDULE_STATE
from openwater.errors import ScheduleValidationException
from openwater.schedule.helpers import (
    insert_schedule,
    update_schedule,
    delete_schedule,
)
from openwater.schedule.model import ProgramSchedule
from openwater.schedule.validation import validate_schedule
from openwater.utils.decorator import nonblocking

if TYPE_CHECKING:
    from openwater.core import OpenWater


class ScheduleStore:
    def __init__(self, ow: "OpenWater"):
        self._ow = ow
        self.schedules_: dict = dict()

    @nonblocking
    def updated(self) -> None:
        self._ow.bus.fire(EVENT_SCHEDULE_STATE)

    @property
    def all(self) -> List[ProgramSchedule]:
        return list(self.schedules_.values())

    @nonblocking
    def get(self, id_: int) -> ProgramSchedule:
        return self.schedules_.get(id_, None)

    @nonblocking
    def add(self, schedule: ProgramSchedule) -> None:
        self.schedules_[schedule.id] = schedule
        self.updated()

    @nonblocking
    def remove(self, id_: int):
        try:
            schedule = self.schedules_.pop(id_)
            self.updated()
            return schedule
        except KeyError:
            return None

    async def create(self, data: dict) -> ProgramSchedule:
        errors = validate_schedule(data)
        if errors:
            raise ScheduleValidationException("Schedule failed validation", errors)
        schedule = ProgramSchedule(**data)
        id_ = await insert_schedule(self._ow, schedule.to_db())
        schedule.id = id_
        self.add(schedule)
        return schedule

    async def update(self, data: dict) -> bool:
        errors = validate_schedule(data)
        if errors:
            raise ScheduleValidationException("Schedule failed validation", errors)

        schedule = ProgramSchedule(**data)
        success = await update_schedule(self._ow, schedule.to_db())
        if not success:
            return False
        self.add(schedule)
        return True

    async def delete(self, schedule_id: int) -> bool:
        success = delete_schedule(self._ow, schedule_id)
        if not success:
            return False
        self.remove(schedule_id)
        return True
