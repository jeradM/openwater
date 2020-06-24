from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Dict, Any, List, Optional

if TYPE_CHECKING:
    from openwater.core import OpenWater


class ZoneRun:
    def __init__(self, id: int, zone_id: int, start: datetime, duration: int):
        self.id = id
        self.zone_id = zone_id
        self.start = start
        self.duration = duration

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "zone_id": self.zone_id,
            "start": self.start,
            "duration": self.duration,
        }

    def to_db(self) -> dict:
        return self.to_dict()


class BaseZone(ABC):
    def __init__(
        self,
        ow: "OpenWater",
        id: int,
        name: str,
        zone_type: str,
        is_master: bool,
        attrs: dict,
        open_offset: int = 0,
        close_offset: int = 0,
        last_run: Optional[ZoneRun] = None,
    ):
        self._ow = ow
        self.id = id
        self.name = name
        self.zone_type = zone_type
        self.is_master = is_master
        self.attrs = attrs
        self.open_offset = open_offset
        self.close_offset = close_offset
        self.last_run = last_run
        self.master_zones: Optional[List[BaseZone]] = None

    @classmethod
    def of(cls, ow: "OpenWater", data: Dict[str, Any]):
        return cls(
            ow=ow,
            id=data.get("id"),
            name=data["name"],
            zone_type=data["zone_type"],
            is_master=data["is_master"],
            open_offset=data["open_offset"],
            close_offset=data["close_offset"],
            attrs=data["attrs"],
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "zone_type": self.zone_type,
            "is_master": self.is_master,
            "open_offset": self.open_offset,
            "close_offset": self.close_offset,
            "open": self.is_open(),
            "attrs": dict(self.attrs, **self.extra_attrs),
            "last_run": self.last_run,
            "master_zones": self.master_zones,
        }

    def to_db(self):
        return {
            "id": self.id,
            "name": self.name,
            "zone_type": self.zone_type,
            "is_master": self.is_master,
            "open": self.is_open(),
            "attrs": dict(self.attrs, **self.extra_attrs),
        }

    @abstractmethod
    def is_open(self) -> bool:
        pass

    @abstractmethod
    async def open(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    def get_zone_type(self) -> str:
        pass

    @property
    def extra_attrs(self) -> dict:
        return {}

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
