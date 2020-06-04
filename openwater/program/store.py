from typing import TYPE_CHECKING, Set, Dict, Collection

from openwater.constants import EVENT_ZONE_ADDED
from openwater.database import model
from openwater.errors import ProgramException
from openwater.program.helpers import (
    insert_program,
    update_program,
    get_program_schedules,
)
from openwater.program.model import BaseProgram, ProgramSchedule
from openwater.program.registry import ProgramRegistry
from openwater.utils.decorator import nonblocking

if TYPE_CHECKING:
    from openwater.core import OpenWater


class ProgramStore:
    def __init__(self, ow: "OpenWater", registry: ProgramRegistry):
        self._ow = ow
        self._registry = registry
        self.programs_: dict = dict()

    @property
    def programs(self):
        return list(self.programs_.values())

    @nonblocking
    def get_program(self, id_: int) -> BaseProgram:
        """Get a program from the store by id"""
        program = self.programs_.get(id_, None)
        return program

    async def get_schedules(self, program_id: int) -> Collection[ProgramSchedule]:
        return await get_program_schedules(self._ow, program_id)

    @nonblocking
    def add_program(self, program: BaseProgram) -> None:
        """Add a new program to the store"""
        z = self.get_program(program.id)
        if z:
            raise ProgramException("Program {} already exists")
        self.programs_[program.id] = program

    @nonblocking
    def remove_program(self, program: BaseProgram) -> None:
        """Remove a program from the store"""
        if program not in self.programs_:
            raise ProgramException("Zone {} not found".format(program.id))
        self.programs_.pop(program.id)

    async def create_program(self, data: Dict) -> BaseProgram:
        """Create a new zone and insert database record"""
        id_ = await insert_program(self._ow, data)

        program_type = self._registry.get_program_for_type(data["program_type"])
        program = program_type.create(self._ow, data)
        program.id = id_

        self._ow.bus.fire(EVENT_ZONE_ADDED, program.to_dict())
        self.programs_[id_] = program

        return program

    async def update_program(self, data: Dict) -> BaseProgram:
        """Update an existing program and update database record"""
        await update_program(self._ow, data)

        program_type = self._registry.get_program_for_type(data["program_type"])
        program = program_type.create(self._ow, data)
        self.programs_[program.id] = program
        return program

    async def delete_program(self, program: BaseProgram):
        """Delete a program from the store and remove database record"""
        query = model.program.delete().where(model.program.c.id == program.id)
        con = self._ow.db.connection
        await con.execute(query=query)
        self.remove_program(program)
