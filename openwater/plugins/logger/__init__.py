import logging
from typing import Optional

from openwater.database import DatabaseLoggingHandler

_STR_TO_LEVEL = {
    "NONE": logging.NOTSET,
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARN": logging.WARN,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def get_level(level: Optional[str]) -> int:
    if level is None:
        return logging.ERROR
    level_ = level.upper()
    if level_ not in _STR_TO_LEVEL:
        return logging.ERROR
    return _STR_TO_LEVEL[level_]


def setup_plugin(ow: "OpenWater", config: dict):
    formatter = logging.Formatter(config.get("format", logging.BASIC_FORMAT))
    root = logging.getLogger()
    root.setLevel(config.get("default"))
    hndlr = root.handlers[0]
    hndlr.setFormatter(formatter)

    if config.get("database", False) is True:
        db_handler = DatabaseLoggingHandler(ow)
        root.addHandler(db_handler)

    for logger, level in config.get("loggers", {}).items():
        logging.getLogger(logger).setLevel(get_level(level))
