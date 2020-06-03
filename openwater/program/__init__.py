from typing import TYPE_CHECKING

from openwater.program.controller import ProgramController
from openwater.program.registry import ProgramRegistry
from openwater.program.store import ProgramStore

if TYPE_CHECKING:
    from openwater.core import OpenWater


class ProgramManager:
    def __init__(self, ow: "OpenWater"):
        self.registry = ProgramRegistry()
        self.store = ProgramStore(ow, self.registry)
        self.controller = ProgramController(ow)
