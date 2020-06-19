from datetime import datetime
from typing import Optional

from cerberus import Validator
from cerberus.errors import ErrorList

to_date = lambda s: datetime.strptime(s, "%Y-%m-%d")


STEP_SCHEMA = {
    "id": {"type": "integer", "nullable": True},
    "program_id": {"type": "integer", "nullable": True},
    "duration": {"type": "integer", "required": True, "min": 1},
    "order": {"type": "integer", "required": True},
    "zones": {"type": "list"},
}


SCHEDULE_SCHEMA = {
    "id": {"type": "integer", "nullable": True},
    "program_id": {"type": "integer", "nullable": True},
    "name": {"type": "string", "nullable": True},
    "enabled": {"type": "boolean", "required": True},
    "at": {"type": "integer", "required": True},
    "day_interval": {"type": "integer", "nullable": True},
    "days_restriction": {
        "type": "string",
        "nullable": True,
        "allowed": ["E", "O", None],
    },
    "dow_mask": {"type": "integer", "nullable": True, "min": 0, "max": 127},
    "minute_interval": {"type": "integer", "nullable": True},
    "on_day": {"type": "date", "nullable": True, "coerce": to_date},
    "start_day": {"type": "date", "nullable": True, "coerce": to_date},
    "schedule_type": {"type": "string", "required": True},
}


PROGRAM_SCHEMA = {
    "id": {"type": "integer", "nullable": True},
    "name": {"type": "string", "minlength": 1, "maxlength": 100, "required": True},
    "program_type": {"type": "string", "required": True},
    "attrs": {"type": "dict", "required": True, "nullable": True},
    "schedules": {
        "type": "list",
        "schema": {"type": "dict", "schema": SCHEDULE_SCHEMA},
    },
    "steps": {"type": "list", "schema": {"type": "dict", "schema": STEP_SCHEMA}},
}


def validate_program(data: dict) -> Optional["ErrorList"]:
    validator: Validator = Validator(PROGRAM_SCHEMA)
    if not validator.validate(data):
        return validator.errors
    return None
