from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Collection, Optional


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

    @property
    def step_type(self):
        raise NotImplementedError


class ZoneStep(BaseStep):
    """Defines when and for how long a zone should run and tracks a zone's progress"""

    def __init__(self, zone_id: int, duration: int):
        super().__init__(duration)
        self.zone_id = zone_id

    @property
    def step_type(self):
        return "ZONE"


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
