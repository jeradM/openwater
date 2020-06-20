from typing import Optional

from cerberus import Validator
from cerberus.errors import ErrorList

STEP_SCHEMA = {
    "id": {"type": "integer", "nullable": True},
    "program_id": {"type": "integer", "nullable": True},
    "duration": {"type": "integer", "required": True, "min": 1},
    "order": {"type": "integer", "required": True},
    "zones": {"type": "list"},
}


PROGRAM_SCHEMA = {
    "id": {"type": "integer", "nullable": True},
    "name": {"type": "string", "minlength": 1, "maxlength": 100, "required": True},
    "program_type": {"type": "string", "required": True},
    "attrs": {"type": "dict", "required": True, "nullable": True},
    "steps": {"type": "list", "schema": {"type": "dict", "schema": STEP_SCHEMA}},
}


def validate_program(data: dict) -> Optional["ErrorList"]:
    validator: Validator = Validator(PROGRAM_SCHEMA)
    if not validator.validate(data):
        return validator.errors
    return None
