import copy
from typing import Optional, Type, Any, Dict

from cerberus import Validator
from cerberus.errors import ErrorList

from openwater.zone.model import BaseZone

ZONE_SCHEMA = {
    "id": {"type": "integer"},
    "name": {"type": "string", "maxlength": 100, "required": True},
    "zone_type": {"type": "string", "maxlength": 50, "required": True},
    "is_master": {"type": "boolean", "required": True},
    "attrs": {"type": "dict", "required": True},
}
ATTR_SCHEMA = {
    "soil_type": {"type": "string"},
    "precip_rate": {"type": "float"},
}


def validate_zone(self, data: dict) -> Optional["ErrorList"]:
    validator = Validator(ZONE_SCHEMA)
    if not validator.validate(data):
        return validator.errors
    return None


def validate_attrs(self, zone_cls: Type[BaseZone], data: dict) -> Optional["ErrorList"]:
    schema: Dict[str, Any] = copy.deepcopy(ATTR_SCHEMA)
    if hasattr(zone_cls, "ATTR_SCHEMA"):
        schema.update(getattr(zone_cls, "ATTR_SCHEMA"))
    validator = Validator(ZONE_SCHEMA)
    if not validator.validate(data):
        return validator.errors
    return None
