import logging
from typing import TYPE_CHECKING, Optional

from openirrigation.constants import EVENT_TIMER_TICK_MIN, EVENT_TIMER_TICK_SEC, EVENT_PROGRAM_COMPLETED
from openirrigation.model import BaseProgram

if TYPE_CHECKING:
    from openirrigation.core import OpenIrrigation, Event

_LOGGER = logging.getLogger(__name__)


async def setup_plugin(oi: OpenIrrigation) -> None:
    scheduler = Scheduler(oi)
    setattr(oi, 'scheduler', scheduler)


class Scheduler:
    def __init__(self, oi: OpenIrrigation):
        self.oi = oi
        self.running_program: Optional[BaseProgram] = None
        oi.bus.listen(EVENT_TIMER_TICK_MIN, self.schedule_program)
        oi.bus.listen(EVENT_PROGRAM_COMPLETED, self.program_complete)

    async def schedule_program(self, event: Event):
        if self.running_program is not None:
            return

        programs = self.oi.programs
        ready = [p for p in programs if p.should_run(event.data['now'])]
        if not ready:
            _LOGGER.debug('No programs scheduled to run')
            return

        next_program = sorted(ready, key=lambda x: x.priority)[0]
        self.running_program = next_program

    def program_complete(self, event: Event):
        program: BaseProgram = event.data['program']
        if program.pid != self.running_program.pid:
            _LOGGER.error('Completed program did not match running program')

        self.running_program = None

    async def check_program_progress(self, event):
        if self.running_program is None:
            return

        event_data = event['data']
        now = event_data['now']



