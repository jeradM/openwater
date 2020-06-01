import logging
from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Collection,
    Dict,
    Type,
    Set,
    Callable,
)

from openwater.constants import EVENT_ZONE_ADDED, EVENT_ZONE_UPDATED
from openwater.database import model
from openwater.errors import (
    ZoneRegistrationException,
    OWError,
    ZoneException,
)

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


async def load_zones(ow: "OpenWater"):
    if not ow.db:
        raise OWError("OpenWater database not initialized")

    rows = await ow.db.connection.fetch_all(query=model.zone.select())
    for row in rows:
        zone = dict(row)
        zone_type = ow.zones.registry.get_zone_for_type(zone["zone_type"])
        if zone_type is None:
            continue
        z = zone_type.create(ow, zone)
        ow.zones.store.add_zone(z)


async def insert_zone(ow: "OpenWater", data: dict) -> int:
    conn = ow.db.connection
    new_id = await conn.execute(query=model.zone.insert(), values=data)
    return new_id


async def update_zone(ow: "OpenWater", data: dict):
    conn = ow.db.connection
    await conn.execute(query=model.zone.update(), values=data)


async def delete_zone(ow: "OpenWater", id_: int):
    conn = ow.db.connection
    query = model.zone.delete().where(model.zone.c.id == id_)
    await conn.execute(query=query)


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


class ZoneController:
    def __init__(self, ow: "OpenWater", store: "ZoneStore"):
        self._ow = ow
        self._store = store
        self.zone_types: Dict[str, Dict] = {}
        self.zones: Dict[int, BaseZone] = {}

    async def open_zone(self, zone_id: int):
        target = self._store.get_zone(zone_id)
        if target is None:
            _LOGGER.error("Requested to open a non-existent zone: {}".format(zone_id))
            return
        await target.open()
        self._ow.bus.fire(EVENT_ZONE_UPDATED, target.to_dict())

    async def close_zone(self, zone_id: int):
        target = self._store.get_zone(zone_id)
        if target is None:
            _LOGGER.error("Requested to close a non-existent zone: {}".format(zone_id))
            return
        await target.close()
        self._ow.bus.fire(EVENT_ZONE_UPDATED, target.to_dict())

    async def close_zones(self, zone_ids: Collection[int]):
        for zone_id in zone_ids:
            await self.close_zone(zone_id)


class RegisteredZoneType:
    def __init__(
        self, cls: Type[BaseZone], create_func: Callable[["OpenWater", dict], BaseZone]
    ):
        self.cls = cls
        self.create = create_func


class ZoneRegistry:
    def __init__(self):
        self.zone_types: Dict[str, RegisteredZoneType] = dict()

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

        self.zone_types[zone_type] = RegisteredZoneType(cls, create_func)
        _LOGGER.debug("Registered zone type {}:{}".format(zone_type, cls))

    def unregister_zone_type(self, zone_type: str) -> None:
        if zone_type in self.zone_types:
            self.zone_types.pop(zone_type)
            _LOGGER.debug("Unregistered zone type: {}".format(zone_type))

    def get_zone_for_type(self, zone_type: str) -> RegisteredZoneType:
        if zone_type not in self.zone_types:
            raise ZoneException("Zone type not found: {}".format(zone_type))

        return self.zone_types[zone_type]


class ZoneStore:
    def __init__(self, ow: "OpenWater", registry: "ZoneRegistry"):
        self._ow = ow
        self._registry = registry
        self.zones: Set[BaseZone] = set()

    def get_zone(self, id_: int):
        """Get a zone from the store by id"""
        zone = next((z for z in self.zones if z.id == id_), None)
        return zone

    def add_zone(self, zone: BaseZone):
        """Add a new zone to the store"""
        z = self.get_zone(zone.id)
        if z:
            raise ZoneException("Zone {} already exists")
        self.zones.add(zone)

    def remove_zone(self, zone: BaseZone):
        """Remove a zone from the store"""
        if zone not in self.zones:
            raise ZoneException("Zone {} not found".format(zone.id))
        self.zones.remove(zone)

    async def create_zone(self, data: Dict) -> BaseZone:
        """Create a new zone and insert database record"""
        id_ = await insert_zone(self._ow, data)

        zone_type = self._registry.get_zone_for_type(data["zone_type"])
        zone = zone_type.create(self._ow, data)
        zone.id = id_

        self._ow.bus.fire(EVENT_ZONE_ADDED, zone.to_dict())
        self.zones.add(zone)

        return zone

    async def update_zone(self, data: Dict) -> BaseZone:
        """Update an existing zone and update database record"""
        await update_zone(self._ow, data)

        zone_type = self._registry.get_zone_for_type(data["zone_type"])
        zone = zone_type.create(self._ow, data)
        self.zones.add(zone)
        return zone

    async def delete_zone(self, zone: BaseZone):
        """Delete a zone from the store and remove database record"""
        query = model.zone.delete().where(model.zone.c.id == zone.id)
        con = self._ow.db.connection
        await con.execute(query=query)
        self.remove_zone(zone)


class ZoneManager:
    def __init__(self, ow: "OpenWater"):
        self.registry = ZoneRegistry()
        self.store = ZoneStore(ow, self.registry)
        self.controller = ZoneController(ow, self.store)
