import logging
from abc import abstractmethod, ABC
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional, Callable, Collection, Type, Dict, Set

from openwater.constants import EVENT_TIMER_TICK_SEC, EVENT_PROGRAM_COMPLETED
from openwater.database import model
from openwater.errors import ProgramException, OWError

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


async def load_programs(ow: "OpenWater"):
    if not ow.db:
        raise OWError("OpenWater database not initialized")

    rows = await ow.db.connection.fetch_all(query=model.program.select())
    for row in rows:
        program = dict(row)
        program_type = ow.programs.registry.get_program_for_type(
            program["program_type"]
        )
        if program_type is None:
            continue
        z = program_type.create(ow, program)
        ow.programs.store.add_zone(z)


async def insert_program(ow: "OpenWater", data: dict) -> int:
    conn = ow.db.connection
    new_id = await conn.execute(query=model.program.insert(), values=data)
    return new_id


async def update_program(ow: "OpenWater", data: dict):
    conn = ow.db.connection
    await conn.execute(query=model.program.update(), values=data)


async def delete_program(ow: "OpenWater", id_: int):
    conn = ow.db.connection
    query = model.program.delete().where(model.program.c.id == id_)
    await conn.execute(query=query)


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
        self.ow.bus.fire(
            EVENT_PROGRAM_COMPLETED, data={"program": self, "now": datetime.now()}
        )

    async def check_progress(self):
        current_step = self.steps[self.current_step_idx]

        for step in current_step.steps:
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


class RegisteredProgramType:
    def __init__(
        self,
        cls: Type[BaseProgram],
        create_func: Callable[["OpenWater", dict], BaseProgram],
    ):
        self.cls = cls
        self.create = create_func


class ProgramRegistry:
    def __init__(self):
        self.program_types: Dict[str, RegisteredProgramType] = dict()

    def register_program_type(
        self, program_type: str, cls: Type[BaseProgram], create_func: Callable
    ) -> None:
        if program_type in self.program_types:
            _LOGGER.error(
                "Attempting to register duplicate zone type: {}".format(program_type)
            )
            raise ProgramException(
                "Program type '{}' has already been registered".format(program_type)
            )

        self.program_types[program_type] = RegisteredProgramType(cls, create_func)
        _LOGGER.debug("Registered program type {}:{}".format(program_type, cls))

    def unregister_program_type(self, program_type: str) -> None:
        if program_type in self.program_types:
            self.program_types.pop(program_type)
            _LOGGER.debug("Unregistered program type: {}".format(program_type))

    def get_program_for_type(self, program_type: str) -> RegisteredProgramType:
        if program_type not in self.program_types:
            raise ProgramException("Program type not found: {}".format(program_type))

        return self.program_types[program_type]


class ProgramStore:
    def __init__(self, ow: "OpenWater", registry: ProgramRegistry):
        self._ow = ow
        self._registry = registry
        self.programs: Set[BaseProgram] = set()

    def get_program(self, id_: int) -> BaseProgram:
        """Get a program from the store by id"""
        program = next(z for z in self.programs if z.id == id_)
        if program is None:
            raise ProgramException("Program not found: {}".format(id_))
        return program

    def add_program(self, program: BaseProgram) -> None:
        """Add a new program to the store"""
        z = self.get_program(program.id)
        if z:
            raise ProgramException("Program {} already exists")
        self.programs.add(program)

    def remove_program(self, program: BaseProgram) -> None:
        """Remove a program from the store"""
        if program not in self.programs:
            raise ProgramException("Zone {} not found".format(program.id))
        self.programs.remove(program)

    async def create_program(self, data: Dict) -> BaseProgram:
        """Create a new zone and insert database record"""
        id_ = await insert_program(self._ow, data)

        program_type = self._registry.get_program_for_type(data["program_type"])
        program = program_type.create(self._ow, data)
        program.id = id_

        self._ow.bus.fire(EVENT_ZONE_ADDED, zone.to_dict())
        self.programs.add(program)

        return program

    async def update_program(self, data: Dict) -> BaseProgram:
        """Update an existing program and update database record"""
        await update_program(self._ow, data)

        program_type = self._registry.get_program_for_type(data["program_type"])
        program = program_type.create(self._ow, data)
        self.programs.add(program)
        return program

    async def delete_program(self, program: BaseProgram):
        """Delete a program from the store and remove database record"""
        query = model.program.delete().where(model.program.c.id == program.id)
        con = self._ow.db.connection
        await con.execute(query=query)
        self.remove_program(program)


class ProgramManager:
    def __init__(self, ow: "OpenWater"):
        self.registry = ProgramRegistry()
        self.store = ProgramStore(ow, self.registry)
        self.controller = ProgramController(ow)
