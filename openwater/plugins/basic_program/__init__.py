from datetime import datetime
from typing import TYPE_CHECKING

from openwater.program.model import BaseProgram
from openwater.utils.decorator import nonblocking

if TYPE_CHECKING:
    from openwater.core import OpenWater

PROGRAM_TYPE_BASIC = "Basic"


@nonblocking
def setup_plugin(ow: "OpenWater", config: dict = {}):
    ow.programs.registry.register_program_type(
        PROGRAM_TYPE_BASIC, BasicProgram, create_program
    )


@nonblocking
def create_program(ow: "OpenWater", data: dict) -> "BasicProgram":
    return BasicProgram(id=data["id"], name=data["name"])


class BasicProgram(BaseProgram):
    pass
