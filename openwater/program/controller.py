import asyncio
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Callable

from openwater.constants import EVENT_TIMER_TICK_SEC, EVENT_PROGRAM_COMPLETED
from openwater.program.model import (
    BaseProgram,
    ProgramStep,
)
from openwater.utils.decorator import nonblocking

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


class ProgramController:
    def __init__(self, ow: "OpenWater"):
        self.ow = ow
        self.current_program: Optional[BaseProgram] = None
        self.current_run_id: Optional[int] = None
        self.current_step_idx: Optional[int] = None
        self.current_step: Optional[ProgramStep] = None
        self.remove_listener_sec: Optional[Callable] = None

    async def run_program(self, program: BaseProgram) -> None:
        _LOGGER.debug("Running program %d: %s", program.id, program.name)
        self.current_program = program
        await self.next_step()

    @nonblocking
    def program_complete(self):
        _LOGGER.debug(
            "Completed program %d: %s",
            self.current_program.id,
            self.current_program.name,
        )
        self.remove_listener_sec()
        self.ow.bus.fire(
            EVENT_PROGRAM_COMPLETED, data={"program": self, "now": datetime.now()}
        )

    async def check_progress(self, event):
        step = self.current_step
        _LOGGER.debug("Checking program progress: Step: %d", step.id)

        open_mzs = step.check_open_master_zones()
        for mz in open_mzs:
            self.ow.fire_coroutine(self.ow.zones.controller.open_zone(mz))

        next_step = self.get_next_step()
        if next_step:
            close_mzs = step.check_close_master_zones(next_step.master_zones)
            for mz in close_mzs:
                self.ow.fire_coroutine(self.ow.zones.controller.close_zone(mz))

        if not step.is_complete():
            _LOGGER.debug("Step not complete: %d", step.id)
            return

        _LOGGER.debug("Step complete: %d", step.id)
        if step.running:
            next_mzs = next_step.master_zones if next_step is not None else []
            for zone in step.zones:
                await self.ow.zones.controller.close_zone(zone.id)
                _LOGGER.debug(
                    "Current mzs: %s - Next mzs: %s", zone.master_zones, next_mzs
                )
                mzs = set(zone.master_zones) if zone.master_zones is not None else set()
                for mz in list(mzs - set(next_mzs)):
                    _LOGGER.debug(
                        "Master zone %d should close: %s - offset: %s",
                        mz.id,
                        mz.name,
                        mz.close_offset,
                    )
                    if not mz.is_open():
                        continue
                    if mz.close_offset <= 0:
                        _LOGGER.debug("Closing master zone")
                        self.ow.fire_coroutine(
                            self.ow.zones.controller.close_zone(mz.id)
                        )
                    else:
                        _LOGGER.debug("Closing master in %d sec", mz.close_offset)
                        self.ow.run_coroutine_in(
                            self.ow.zones.controller.close_zone(mz.id), mz.close_offset
                        )

        step.end()
        _LOGGER.debug("Program step %d finished", self.current_step_idx)
        await self.next_step()

    async def complete_step(self):
        pass

    def get_next_step(self) -> Optional[ProgramStep]:
        next_step_idx = self.current_step_idx + 1
        if len(self.current_program.steps) <= next_step_idx:
            return None
        return self.current_program.steps[next_step_idx]

    async def next_step(self):
        _LOGGER.debug("Running next step")
        next_step_idx = (
            self.current_step_idx + 1 if self.current_step_idx is not None else 0
        )
        if len(self.current_program.steps) <= next_step_idx:
            _LOGGER.debug("No next step - program complete")
            self.program_complete()
            return
        next_step = self.current_program.steps[next_step_idx]
        open_mzs = next_step.check_open_master_zones()
        await asyncio.gather(
            *[self.ow.zones.controller.open_zone(zone.id) for zone in next_step.zones]
        )
        next_step.start()
        if self.current_step:
            _LOGGER.debug("Current: %d - Next: %d", self.current_step.id, next_step.id)
        self.current_step_idx = next_step_idx
        self.current_step = next_step
        if self.remove_listener_sec is None:
            self.remove_listener_sec = self.ow.bus.listen(
                EVENT_TIMER_TICK_SEC, self.check_progress
            )
