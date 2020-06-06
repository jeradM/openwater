import logging
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Collection, Callable

from openwater.constants import EVENT_TIMER_TICK_SEC, EVENT_PROGRAM_COMPLETED
from openwater.program.model import BaseProgram, ProgramStep

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


class ProgramController:
    def __init__(self, ow: "OpenWater"):
        self.ow = ow
        self.current_program: Optional[BaseProgram] = None
        self.steps: Optional[Collection[ProgramStep]] = None
        self.current_step_idx: Optional[int] = None
        self.remove_listener: Optional[Callable] = None

    async def queue_program(self, program: BaseProgram):
        self.current_program = program
        self.steps = program.steps

    async def start(self):
        self.remove_listener = self.ow.bus.listen(
            EVENT_TIMER_TICK_SEC, self.check_progress
        )
        await self.next_step()

    async def program_complete(self):
        _LOGGER.debug("Program complete")
        self.remove_listener()
        self.ow.bus.fire(
            EVENT_PROGRAM_COMPLETED, data={"program": self, "now": datetime.now()}
        )

    async def check_progress(self):
        current_step = self.steps[self.current_step_idx]

        for step in current_step.actions:
            if step.running and step.is_complete():
                await self.ow.zones.controller.close_zone(step.zone_id)
                step.end()

        if not current_step.is_complete():
            return

        current_step.end()
        _LOGGER.debug("Program step {} finished".format(self.current_step_idx))
        await self.next_step()

    async def complete_step(self):
        pass

    async def next_step(self):
        next_step_idx = (
            self.current_step_idx + 1 if self.current_step_idx is not None else 0
        )
        if len(self.current_program.get_steps()) <= next_step_idx:
            await self.program_complete()
            return
        next_step = self.steps[next_step_idx]
        self.current_step_idx = next_step_idx
        for step in next_step.steps:
            if not step.zone_id:
                continue
            await self.ow.zones.controller.open_zone(step.zone_id)
        next_step.start()
