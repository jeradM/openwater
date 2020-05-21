import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any

from openirrigation.database.model import MZone

_LOGGER = logging.getLogger(__name__)


class BaseZone(ABC):
    def __init__( self, zone_id: int, name: str, active: bool, **kwargs: Any):
        self.zone_id = zone_id
        self.name = name
        self.active = active
        self.attrs = kwargs

    @classmethod
    def from_db(cls, db_zone: MZone):
        return cls(
            zone_id=db_zone.id,
            name=db_zone.name,
            active=db_zone.active,
            soil_type=db_zone.soil_type,
            precip_rate=db_zone.precip_rate
        )

    @abstractmethod
    async def turn_on(self) -> None:
        pass

    @abstractmethod
    async def turn_off(self) -> None:
        pass

    @abstractmethod
    def get_zone_type(self) -> str:
        pass


class BaseProgram(ABC):
    def __init__(self, pid: int, name: str, start_at: datetime):
        self.pid = pid
        self.name = name
        self.start_at = start_at
        self.is_running = False

    @abstractmethod
    async def should_run(self, now: datetime) -> bool:
        pass

    @abstractmethod
    async def run(self):
        pass

    @abstractmethod
    async def stop(self):
        pass
