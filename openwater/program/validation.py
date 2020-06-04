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
