from typing import TYPE_CHECKING, Dict, List, Optional

from openwater.constants import EVENT_PROGRAM_STATE
from openwater.errors import ProgramException, ProgramValidationException
from openwater.program.helpers import (
    insert_program,
    update_program,
    delete_program,
)
from openwater.program.model import BaseProgram, ProgramStep
from openwater.program.registry import ProgramRegistry
from openwater.program.validation import validate_program
from openwater.utils.decorator import nonblocking

if TYPE_CHECKING:
    from openwater.core import OpenWater


class ProgramStore:
    def __init__(self, ow: "OpenWater", registry: ProgramRegistry):
        self._ow = ow
        self._registry = registry
        self.programs_: dict = dict()
        self.steps_: dict = dict()

    @nonblocking
    def to_dict(self):
        return {"programs": self.all, "steps": self.steps}

    @property
    def all(self) -> List[BaseProgram]:
        return list(self.programs_.values())

    @property
    def steps(self) -> List[ProgramStep]:
        return list(self.steps_.values())

    @nonblocking
    def get(self, id_: int) -> Optional[BaseProgram]:
        """Get a program from the store by id"""
        return self.programs_.get(id_, None)

    @nonblocking
    def add(self, program: BaseProgram) -> None:
        """Add a new program to the store"""
        self.programs_[program.id] = program
        self._ow.bus.fire(EVENT_PROGRAM_STATE, program)

    @nonblocking
    def remove(self, id_: int) -> None:
        """Remove a program from the store"""
        try:
            res = self.programs_.pop(id_)
            self._ow.bus.fire(EVENT_PROGRAM_STATE, program)
            return res
        except KeyError:
            return None

    async def create(self, data: Dict) -> BaseProgram:
        """Create a new zone and insert database record"""

        errors = validate_program(data)
        if errors:
            raise ProgramValidationException("Program validation failed", errors)

        id_ = await insert_program(self._ow, data)
        data["id"] = id_
        program_type = self._registry.get_program_for_type(data["program_type"])
        program = program_type.create(self._ow, data)
        self.add(program)

        return program

    async def update(self, data: Dict) -> BaseProgram:
        """Update an existing program and update database record"""
        errors = validate_program(data)
        if errors:
            raise ProgramValidationException("Program validation failed", errors)

        await update_program(self._ow, data)

        program_type = self._registry.get_program_for_type(data["program_type"])
        program = program_type.create(self._ow, data)
        self.add(program)

        return program

    async def delete(self, program_id: int):
        """Delete a program from the store and remove database record"""
        success = delete_program(self._ow, program_id)
        if success:
            self.remove(program_id)
        return success
