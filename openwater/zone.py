import logging
from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Collection,
    Dict,
    Type,
    Set,
    List,
    Optional,
    Callable,
)

from openwater.constants import EVENT_ZONE_ADDED, EVENT_ZONE_UPDATED
from openwater.database import model
from openwater.errors import ZoneRegistrationException, OWError, ZoneException

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


async def load_zones(ow: "OpenWater"):
    if not ow.db:
        raise OWError("OpenWater database not initialized")

    rows = await ow.db.connection.fetch_all(query=model.zone.select())
    for row in rows:
        zone = dict(row)
        zone_type = ow.zone_controller.get_zone_for_type(zone["zone_type"])
        if zone_type is None:
            continue
        z = zone_type["create_func"](ow, zone)
        ow.zone_controller.zones[z.id] = z


async def add_zone(ow: "OpenWater", zone: "BaseZone"):
    conn = ow.db.connection
    res = await conn.execute(query=model.zone.insert(), values=zone.to_dict())
    zone.id = res
    ow.bus.async_fire(EVENT_ZONE_ADDED, zone.to_dict())
    return zone


async def update_zone(ow: "OpenWater", zone: "BaseZone"):
    conn = ow.db.connection
    data = zone.to_dict()
    res = await conn.execute(query=model.zone.update(), values=data)
    ow.bus.async_fire(EVENT_ZONE_UPDATED, data)


async def save_zone(ow: "OpenWater", zone: "BaseZone"):
    conn = ow.db.connection
    if zone.id:
        query = model.zone.update()
    else:
        query = model.zone.insert()
    data = zone.to_dict()
    return await conn.execute(query=query, values=data)


class BaseZone(ABC):
    def __init__(self, zone_data: dict):
        self.id = zone_data.get("id")
        self.name = zone_data["name"]
        self.active = zone_data["active"]
        self.zone_type = zone_data["zone_type"]
        self.attrs = zone_data.get("attrs", {})

    def to_dict(self):
        d = {
            "id": self.id,
            "name": self.name,
            "active": self.active,
            "zone_type": self.zone_type,
            "open": self.is_open(),
            "attrs": dict(self.attrs, **self.extra_attrs),
        }
        return d

    @abstractmethod
    def is_open(self) -> bool:
        pass

    @abstractmethod
    def open(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def get_zone_type(self) -> str:
        pass

    @property
    def extra_attrs(self) -> dict:
        return {}


class ZoneController:
    def __init__(self, ow: "OpenWater", zones: Collection[BaseZone] = ()):
        self._ow = ow
        self.zone_types: Dict[str, Dict] = {}
        self.zones: Dict[int, BaseZone] = {}

    def get_zone_by_id(self, zone_id: int):
        zone = self.zones.get(zone_id, None)
        if zone is None:
            _LOGGER.debug("Zone not found: {}".format(zone_id))
        return zone

    async def open_zone(self, zone_id: int):
        target = self.get_zone_by_id(zone_id)
        if target is None:
            _LOGGER.error("Requested to open a non-existent zone: {}".format(zone_id))
            return
        target.open()
        self._ow.bus.async_fire(EVENT_ZONE_UPDATED, target.to_dict())

    async def close_zone(self, zone_id: int):
        target = self.get_zone_by_id(zone_id)
        if target is None:
            _LOGGER.error("Requested to close a non-existent zone: {}".format(zone_id))
            return
        target.close()
        self._ow.bus.async_fire(EVENT_ZONE_UPDATED, target.to_dict())

    async def close_zones(self, zone_ids: Collection[int]):
        for zone_id in zone_ids:
            await self.close_zone(zone_id)

    def register_zone_type(
        self, zone_type: str, cls: Type[BaseZone], create_func: Callable
    ) -> None:
        if zone_type in self.zone_types:
            _LOGGER.error(
                "Attempting to register duplicate zone type: {}".format(zone_type)
            )
            raise ZoneRegistrationException(
                "Zone type '{}' has already been registered".format(zone_type)
            )

        self.zone_types[zone_type] = {"cls": cls, "create_func": create_func}
        _LOGGER.debug("Registered zone type {}".format(zone_type))

    def unregister_zone_type(self, zone_type) -> None:
        if zone_type in self.zone_types:
            self.zone_types.pop(zone_type)
            _LOGGER.debug("Unregistered zone type: {}".format(zone_type))

    def get_zone_for_type(self, zone_type: str) -> Optional[Dict]:
        if zone_type not in self.zone_types:
            _LOGGER.error("Zone type not found: {}".format(zone_type))
            return None

        return self.zone_types[zone_type]

    def get_all_registered_types(self) -> List[str]:
        return list(self.zone_types.keys())

    async def create_zone(self, zone_data: dict) -> BaseZone:
        zone_type = self.get_zone_for_type(zone_data["zone_type"])
        zone = zone_type["create_func"](self._ow, zone_data)
        zone = await add_zone(self._ow, zone)
        self.zones[zone.id] = zone
        return zone

    async def update_zone(self, zone_data: dict) -> BaseZone:
        id_ = zone_data["id"]
        if not id_:
            raise ZoneException("update_zone: no zone id provided")
        zone = self.get_zone_by_id(id_)
        if not zone:
            raise ZoneException("update_zone: zone not found for id {}".format(id_))
        await save_zone(self._ow, zone)
        return zone
