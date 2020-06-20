from datetime import datetime
from typing import Optional

from cerberus import Validator
from cerberus.errors import ErrorList


def to_date(d):
    return datetime.strptime(d, "%Y-%m-%d")


SCHEDULE_SCHEMA = {
    "id": {"type": "integer", "nullable": True},
    "program_id": {"type": "integer", "required": True},
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
    "schedule_type": {
        "type": "string",
        "required": True,
        "allowed": ["Weekly", "Interval", "Single"],
    },
}


def validate_schedule(data: dict) -> Optional["ErrorList"]:
    validator: Validator = Validator(SCHEDULE_SCHEMA)
    if not validator.validate(data):
        return validator.errors
    return None
