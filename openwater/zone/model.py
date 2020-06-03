from typing import TYPE_CHECKING, Dict, Any

from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from openwater.core import OpenWater


class BaseZone(ABC):
    def __init__(
        self,
        ow: "OpenWater",
        id_: int,
        name: str,
        zone_type: str,
        is_master: bool,
        attrs: dict,
    ):
        self._ow = ow
        self.id = id_
        self.name = name
        self.zone_type = zone_type
        self.is_master = is_master
        self.attrs = attrs

    @classmethod
    def of(cls, ow: "OpenWater", data: Dict[str, Any]):
        return cls(
            ow=ow,
            id_=data["id"],
            name=data["name"],
            zone_type=data["zone_type"],
            is_master=data["is_master"],
            attrs=data["attrs"],
        )

    def to_dict(self):
        d = {
            "id": self.id,
            "name": self.name,
            "zone_type": self.zone_type,
            "is_master": self.is_master,
            "open": self.is_open(),
            "attrs": dict(self.attrs, **self.extra_attrs),
        }
        return d

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
