from typing import TYPE_CHECKING

from openwater.program.controller import ProgramController
from openwater.program.model import SequentialAction, ParallelAction, SoakAction
from openwater.program.registry import ProgramRegistry
from openwater.program.store import ProgramStore

if TYPE_CHECKING:
    from openwater.core import OpenWater


class ProgramManager:
    def __init__(self, ow: "OpenWater"):
        self.registry = ProgramRegistry()
        self.store = ProgramStore(ow, self.registry)
        self.controller = ProgramController(ow)
        for action in [SequentialAction, ParallelAction, SoakAction]:
            action_type = getattr(action, "ACTION_TYPE")
            self.registry.register_action_type(action_type, action)
