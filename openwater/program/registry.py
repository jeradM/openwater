import logging
from typing import TYPE_CHECKING, Type, Callable, Dict

from openwater.errors import ProgramException
from openwater.program.model import BaseProgram, ProgramAction

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


class RegisteredProgramType:
    def __init__(
        self,
        cls: Type[BaseProgram],
        create_func: Callable[["OpenWater", dict], BaseProgram],
    ):
        self.cls = cls
        self.create = create_func


class ProgramRegistry:
    def __init__(self):
        self.program_types: Dict[str, RegisteredProgramType] = dict()
        self.action_types: Dict[str, ProgramAction] = dict()

    def register_program_type(
        self, program_type: str, cls: Type[BaseProgram], create_func: Callable
    ) -> None:
        if program_type in self.program_types:
            _LOGGER.error(
                "Attempting to register duplicate zone type: {}".format(program_type)
            )
            raise ProgramException(
                "Program type '{}' has already been registered".format(program_type)
            )

        self.program_types[program_type] = RegisteredProgramType(cls, create_func)
        _LOGGER.debug("Registered program type {}:{}".format(program_type, cls))

    def unregister_program_type(self, program_type: str) -> None:
        if program_type in self.program_types:
            self.program_types.pop(program_type)
            _LOGGER.debug("Unregistered program type: {}".format(program_type))

    def get_program_for_type(self, program_type: str) -> RegisteredProgramType:
        if program_type not in self.program_types:
            raise ProgramException("Program type not found: {}".format(program_type))

        return self.program_types[program_type]

    def register_action_type(self, action_type: str, cls: Type[ProgramAction]):
        if action_type in self.action_types:
            raise ProgramException(
                "Action type already registered: {}".format(action_type)
            )
        self.action_types[action_type] = cls

    def unregister_action_type(self, action_type: str):
        if action_type in self.action_types:
            self.action_types.pop(action_type)

    def get_action_type(self, action_type: str):
        if action_type not in self.action_types:
            raise ProgramException("Action type not found: {}".format(action_type))
        return self.action_types[action_type]
