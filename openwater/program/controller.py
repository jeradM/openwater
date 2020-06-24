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
        if self.remove_listener_sec is not None:
            self.remove_listener_sec()
        self.ow.bus.fire(
            EVENT_PROGRAM_COMPLETED, data={"program": self, "now": datetime.now()}
        )

    async def check_progress(self, event):
        step = self.current_step
        _LOGGER.debug("Checking program progress: Step: %d", step.id)

        if not step.is_complete():
            _LOGGER.debug("Step not complete: %d", step.id)
            return

        _LOGGER.debug("Step complete: %d", step.id)
        if step.running:
            await self.finish_step(step)
        step.end()
        _LOGGER.debug("Program step %d finished", self.current_step_idx)
        await self.next_step()

    async def finish_step(self, step: ProgramStep) -> None:
        next_step = self.get_next_step()
        next_masters = next_step.master_zones if next_step else []
        for zone in step.zones:
            await self.ow.zones.controller.close_zone(zone.id)
            if zone.master_zones is None:
                continue
            for mz in zone.master_zones:
                if mz in next_masters:
                    _LOGGER.debug(
                        "Master zone %d will be used in next step - not closing", mz.id
                    )
                    continue
                if mz.close_offset <= 0:
                    _LOGGER.debug("Closing master zone %d now", mz.id)
                    self.ow.fire_coroutine(self.ow.zones.controller.close_zone(mz.id))
                else:
                    _LOGGER.debug(
                        "Closing master zone %d in %d seconds", mz.id, mz.close_offset
                    )
                    self.ow.run_coroutine_in(
                        self.ow.zones.controller.close_zone(mz.id), mz.close_offset,
                    )

    async def complete_step(self):
        pass

    def get_next_step(self) -> Optional[ProgramStep]:
        next_step_idx = self.current_step_idx + 1
        if len(self.current_program.steps) <= next_step_idx:
            return None
        return self.current_program.steps[next_step_idx]

    async def start_step(self, step: ProgramStep) -> None:
        if not step.zones:
            _LOGGER.debug("No zones - Soak step")
            return
        mzs = [
            mz
            for mz in sorted(
                step.master_zones, key=lambda z: z.open_offset, reverse=True
            )
            if not mz.is_open()
        ]
        if not mzs:
            _LOGGER.debug("No master zones in this step - opening zones")
            await asyncio.gather(
                *[self.ow.zones.controller.open_zone(zone.id) for zone in step.zones]
            )
            return
        first = mzs[0]
        _LOGGER.debug("Opening first master zone %d", first.id)
        await self.ow.zones.controller.open_zone(first.id)
        for mz in mzs[1:]:
            diff = first.open_offset - mz.open_offset
            _LOGGER.debug("Opening master %d in %d seconds", mz.id, diff)
            self.ow.run_coroutine_in(
                self.ow.zones.controller.open_zone(mz.id), diff,
            )
        _LOGGER.debug("Waiting %d seconds to open zones", first.open_offset)
        await asyncio.sleep(first.open_offset)
        _LOGGER.debug("Opening zones %s", ",".join([str(z.id) for z in step.zones]))
        await asyncio.gather(
            *[self.ow.zones.controller.open_zone(zone.id) for zone in step.zones]
        )

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
        await self.start_step(next_step)
        next_step.start()
        if self.current_step:
            _LOGGER.debug("Current: %d - Next: %d", self.current_step.id, next_step.id)
        self.current_step_idx = next_step_idx
        self.current_step = next_step
        if self.remove_listener_sec is None:
            self.remove_listener_sec = self.ow.bus.listen(
                EVENT_TIMER_TICK_SEC, self.check_progress
            )
