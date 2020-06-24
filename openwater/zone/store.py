from typing import TYPE_CHECKING, Dict, Optional

from openwater.constants import EVENT_ZONE_STATE
from openwater.errors import ZoneException, ZoneValidationException
from openwater.zone.helpers import insert_zone, update_zone, delete_zone
from openwater.zone.model import BaseZone
from openwater.zone.validation import validate_zone, validate_attrs

if TYPE_CHECKING:
    from openwater.core import OpenWater
    from openwater.zone.registry import ZoneRegistry


class ZoneStore:
    def __init__(self, ow: "OpenWater", registry: "ZoneRegistry"):
        self._ow = ow
        self._registry = registry
        self.zones_ = dict()

    @property
    def all(self):
        return list(self.zones_.values())

    def get(self, id_: int) -> Optional[BaseZone]:
        """Get a zone from the store by id"""
        return self.zones_.get(id_, None)

    def add(self, zone: BaseZone):
        """Add a new zone to the store"""
        self.zones_[zone.id] = zone

    def remove(self, zone: BaseZone):
        """Remove a zone from the store"""
        try:
            return self.zones_.pop(zone.id)
        except KeyError:
            return None

    async def create(self, data: Dict) -> BaseZone:
        """Create a new zone and insert database record"""
        errors = validate_zone(data)
        if errors:
            raise ZoneValidationException("Zone validation failed", errors)
        zone_type = self._registry.get_zone_for_type(data["zone_type"])
        errors = {"attrs": validate_attrs(zone_type.cls, data["attrs"])}
        if errors["attrs"]:
            raise ZoneValidationException("Zone attribute validation failed", errors)
        id_ = await insert_zone(self._ow, data)
        data["id"] = id_
        zone = zone_type.create(self._ow, data)
        self.zones_[zone.id] = zone

        self._ow.bus.fire(EVENT_ZONE_STATE, zone)
        return zone

    async def update(self, data: Dict) -> BaseZone:
        """Update an existing zone and update database record"""
        errors = validate_zone(data)
        if errors:
            raise ZoneValidationException("Zone validation failed", errors)

        zone_type = self._registry.get_zone_for_type(data["zone_type"])
        errors = validate_attrs(zone_type.cls, data["attrs"])
        if errors:
            raise ZoneValidationException("Zone validation failed", errors)

        await update_zone(self._ow, data)
        zone = zone_type.create(self._ow, data)
        zone_ = self.get(data["id"])
        zone.last_run = zone_.last_run
        self.zones_[zone.id] = zone

        self._ow.bus.fire(EVENT_ZONE_STATE, zone)
        return zone

    async def delete(self, zone_id: int) -> int:
        """Delete a zone from the store and remove database record"""
        result = await delete_zone(self._ow, zone_id)
        self.remove(self.get(zone_id))
        self._ow.bus.fire(EVENT_ZONE_STATE, {"zone_id": zone_id})
        return result
