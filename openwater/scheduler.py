import logging
from typing import TYPE_CHECKING, Optional

from openwater.constants import EVENT_TIMER_TICK_MIN, EVENT_PROGRAM_COMPLETED
from openwater.program.model import BaseProgram, ProgramSchedule

if TYPE_CHECKING:
    from openwater.core import OpenWater, Event

_LOGGER = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, ow: "OpenWater"):
        self.ow = ow
        self.running_program: Optional[BaseProgram] = None
        ow.bus.listen(EVENT_TIMER_TICK_MIN, self.check_schedules)
        ow.bus.listen(EVENT_PROGRAM_COMPLETED, self.program_complete)

    async def check_schedules(self, event: "Event"):
        if self.running_program is not None:
            return

        dt = event.data["now"]
        schedules = self.ow.programs.store.schedules
        run_schedule = None
        for schedule in schedules:
            _LOGGER.debug("Checking schedule %s", schedule.id)
            if schedule.matches(dt):
                run_schedule = schedule
                break

        if run_schedule is None:
            _LOGGER.debug("No schedules to run")
            return

        self.running_program = self.ow.programs.store.get_program(
            run_schedule.program_id
        )
        self.ow.fire_coroutine(
            self.ow.programs.controller.run_program(self.running_program)
        )
        _LOGGER.debug(
            "Running program: {} for schedule: {}".format(
                self.running_program, run_schedule
            )
        )

    def program_complete(self, event: "Event"):
        program: BaseProgram = event.data["program"]
        if program.id != self.running_program.pid:
            _LOGGER.error("Completed program did not match running program")

        self.running_program = None

    async def check_program_progress(self, event):
        if self.running_program is None:
            return

        event_data = event["data"]
        now = event_data["now"]
