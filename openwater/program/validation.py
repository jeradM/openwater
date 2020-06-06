PROGRAM_SCHEMA = {
    "id": {"type": "integer"},
    "name": {"type": "string", "minlength": 1, "maxlength": 100, "required": True},
    "active": {"type": "boolean", "required": True},
    "start_time": {"type": "datetime", "required": True},
    "on_days": {"type": "string", "required": True},
    "priority": {"type": "integer"},
    "program_type": {"type": "string", "required": True},
    "attrs": {"type": "dict", "required": True},
}


SCHEDULE_SCHEMA = {
    "id": {"type": "integer"},
    "enabled": {"type": "boolean", "required": True},
    "at": {"type": "integer", "required": True},
    "day_interval": {"type": "integer"},
    "days_restriction": {"type": "string", "allowed": ["E", "O"]},
    "dow_mask": {"type": "integer", "min": 0, "max": 63},
    "minute_interval": {"type": "integer"},
    "on_day": {"type": "date"},
    "start_day": {"type": "date"},
}
