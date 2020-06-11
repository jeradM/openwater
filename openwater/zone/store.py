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
    def zones(self):
        return list(self.zones_.values())

    def get_zone(self, id_: int) -> Optional[BaseZone]:
        """Get a zone from the store by id"""
        zone = self.zones_.get(id_, None)
        return zone

    def add_zone(self, zone: BaseZone):
        """Add a new zone to the store"""
        z = self.get_zone(zone.id)
        if z:
            raise ZoneException("Zone {} already exists")
        self.zones_[zone.id] = zone

    def remove_zone(self, zone: BaseZone):
        """Remove a zone from the store"""
        if zone not in self.zones:
            raise ZoneException("Zone {} not found".format(zone.id))
        self.zones_.pop(zone.id)

    async def create_zone(self, data: Dict) -> BaseZone:
        """Create a new zone and insert database record"""
        errors = validate_zone(data)
        if errors:
            raise ZoneValidationException("Zone validation failed", errors)
        zone_type = self._registry.get_zone_for_type(data["zone_type"])
        errors = {"attrs": validate_attrs(zone_type.cls, data["attrs"])}
        if errors["attrs"]:
            raise ZoneValidationException("Zone attribute validation failed", errors)
        id_ = await insert_zone(self._ow, data)
        zone = zone_type.create(self._ow, data)
        zone.id = id_
        self.zones_[zone.id] = zone

        self._ow.bus.fire(EVENT_ZONE_STATE, zone)
        return zone

    async def update_zone(self, data: Dict) -> BaseZone:
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
        zone_ = self.get_zone(data["id"])
        zone.last_run = zone_.last_run
        self.zones_[zone.id] = zone

        self._ow.bus.fire(EVENT_ZONE_STATE, zone)
        return zone

    async def delete_zone(self, zone_id: int) -> int:
        """Delete a zone from the store and remove database record"""
        result = await delete_zone(self._ow, zone_id)
        self.remove_zone(self.get_zone(zone_id))
        self._ow.bus.fire(EVENT_ZONE_STATE, {"zone_id": zone_id})
        return result
