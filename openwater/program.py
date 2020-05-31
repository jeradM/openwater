import logging
from abc import abstractmethod, ABC
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional, Callable, Collection

from openwater.constants import EVENT_TIMER_TICK_SEC, EVENT_PROGRAM_COMPLETED

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


class BaseProgram(ABC):
    def __init__(self, id_: int, name: str, start_at: datetime):
        self.id = id_
        self.name = name
        self.start_at = start_at
        self.is_running = False

    @abstractmethod
    def get_steps(self) -> Collection["ProgramStep"]:
        pass

    @abstractmethod
    async def should_run(self, now: datetime) -> bool:
        pass

    @abstractmethod
    def to_db_program(self):
        pass


class BaseStep:
    def __init__(self, duration: int):
        self.duration = duration
        self.running = False
        self.done = False
        self.started_at: Optional[datetime] = None
        self.run_until: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def start(self) -> None:
        self.running = True
        self.started_at = datetime.now()
        self.run_until = self.started_at + timedelta(seconds=self.duration)

    def end(self) -> None:
        self.running = False
        self.done = True
        self.completed_at = datetime.now()

    def is_complete(self):
        if self.done:
            return True
        now = datetime.now()
        return (self.run_until - now).total_seconds() < 1


class ZoneStep(BaseStep):
    """Defines when and for how long a zone should run and tracks a zone's progress"""

    def __init__(self, zone_id: int, duration: int):
        super().__init__(duration)
        self.zone_id = zone_id


class ProgramStep:
    """Represents an individual, serial step in a program which can have multiple zones"""

    def __init__(self, steps: Collection[BaseStep]):
        self.steps = steps
        self.done: bool = False
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.running_steps: Optional[Collection[BaseStep]] = None

    def start(self) -> None:
        self.started_at = datetime.now()
        for step in self.steps:
            step.start()

    def end(self) -> None:
        self.done = True
        self.completed_at = datetime.now()

    @property
    def running(self) -> bool:
        return any(s.running for s in self.steps)

    def is_complete(self) -> bool:
        if self.done:
            return True
        return all(s.is_complete() for s in self.steps)


class ProgramController:
    def __init__(self, ow: "OpenWater"):
        self.ow = ow
        self.current_program: Optional[BaseProgram] = None
        self.steps: Optional[Collection[ProgramStep]] = None
        self.current_step_idx: Optional[int] = None
        self.remove_listener: Optional[Callable] = None

    async def queue_program(self, program: BaseProgram):
        self.current_program = program
        self.steps = program.get_steps()

    async def start(self):
        self.remove_listener = self.ow.bus.listen(
            EVENT_TIMER_TICK_SEC, self.check_progress
        )
        await self.next_step()

    async def program_complete(self):
        _LOGGER.debug("Program complete")
        self.remove_listener()
        self.ow.bus.async_fire(
            EVENT_PROGRAM_COMPLETED, data={"program": self, "now": datetime.now()}
        )

    async def check_progress(self):
        current_step = self.steps[self.current_step_idx]

        for step in current_step.steps:
            if step.running and step.is_complete():
                await self.ow.zone_controller.close_zone(step.zone_id)
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
            await self.ow.zone_controller.open_zone(step.zone_id)
        next_step.start()
