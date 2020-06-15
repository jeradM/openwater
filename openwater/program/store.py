from typing import TYPE_CHECKING, Set, Dict, Collection, List

from openwater.database import model
from openwater.errors import ProgramException
from openwater.program.helpers import (
    insert_program,
    update_program,
    get_program_schedules,
    insert_schedule,
    update_schedule,
    delete_program,
    delete_schedule,
)
from openwater.program.model import BaseProgram, ProgramSchedule, ProgramStep
from openwater.program.registry import ProgramRegistry
from openwater.utils.decorator import nonblocking

if TYPE_CHECKING:
    from openwater.core import OpenWater


class ProgramStore:
    def __init__(self, ow: "OpenWater", registry: ProgramRegistry):
        self._ow = ow
        self._registry = registry
        self.programs_: dict = dict()
        self.schedules_: dict = dict()
        self.steps_: dict = dict()

    @property
    def programs(self) -> List[BaseProgram]:
        return list(self.programs_.values())

    @property
    def schedules(self) -> List[ProgramSchedule]:
        return [s for p in self.programs for s in p.schedules]

    @property
    def steps(self) -> List[ProgramStep]:
        return [s for p in self.programs for s in p.steps]

    @nonblocking
    def get_program(self, id_: int) -> BaseProgram:
        """Get a program from the store by id"""
        program = self.programs_.get(id_, None)
        return program

    @nonblocking
    def get_schedule(self, id_: int) -> ProgramSchedule:
        return self.schedules_.get(id_, None)

    @nonblocking
    def add_program(self, program: BaseProgram) -> None:
        """Add a new program to the store"""
        z = self.get_program(program.id)
        if z:
            raise ProgramException("Program {} already exists")
        self.programs_[program.id] = program

    @nonblocking
    def add_schedule(self, schedule: ProgramSchedule) -> None:
        self.schedules_[schedule.id] = schedule

    @nonblocking
    def remove_program(self, id_: int) -> None:
        """Remove a program from the store"""
        if id_ not in self.programs_:
            raise ProgramException("Program {} not found".format(id_))
        self.programs_.pop(id_)

    @nonblocking
    def remove_schedule(self, id_: int):
        if id_ not in self.schedules_:
            raise Exception
        self.schedules_.pop(id_)

    async def create_program(self, data: Dict) -> BaseProgram:
        """Create a new zone and insert database record"""
        id_ = await insert_program(self._ow, data)

        program_type = self._registry.get_program_for_type(data["program_type"])
        program = program_type.create(self._ow, data)
        program.id = id_

        # self._ow.bus.fire(EVENT_ZONE_ADDED, program.to_dict())
        self.programs_[id_] = program

        return program

    async def update_program(self, data: Dict) -> BaseProgram:
        """Update an existing program and update database record"""
        await update_program(self._ow, data)

        program_type = self._registry.get_program_for_type(data["program_type"])
        program = program_type.create(self._ow, data)
        self.programs_[program.id] = program
        return program

    async def delete_program(self, program_id: int):
        """Delete a program from the store and remove database record"""
        success = delete_program(self._ow, program_id)
        if success:
            self.remove_program(program_id)
        return success

    async def get_schedules(self, program_id: int) -> Collection[ProgramSchedule]:
        schedule_data = await get_program_schedules(self._ow, program_id)
        return [ProgramSchedule(**d) for d in schedule_data]

    async def create_schedule(self, data: dict) -> ProgramSchedule:
        id_ = await insert_schedule(self._ow, data)
        schedule = ProgramSchedule(**data)
        schedule.id = id_
        return schedule

    async def update_schedule(self, data: dict) -> bool:
        success = await update_schedule(self._ow, data)
        if not success:
            return False
        self.schedules_[data["id"]] = ProgramSchedule(**data)
        return True

    async def delete_schedule(self, schedule_id: int) -> bool:
        success = delete_schedule(self._ow, schedule_id)
        if success:
            self.schedules_.pop(schedule_id)
        return True
