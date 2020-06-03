import logging
from typing import TYPE_CHECKING, Callable, Type, Dict

from openwater.errors import ZoneRegistrationException, ZoneException
from openwater.zone.model import BaseZone

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


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
