import logging
from typing import Optional


async def setup_plugin(ow: "OpenWater", config: Optional[dict] = {}):
    formatter = logging.Formatter("%(levelname)s - %(name)s - %(message)s")
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    hndlr = root.handlers[0]
    hndlr.setFormatter(formatter)

    logging.getLogger("aiosqlite").setLevel(logging.WARN)
    logging.getLogger("databases").setLevel(logging.WARN)
    # sh = logging.StreamHandler()
    # sh.setFormatter(formatter)
    # sh.setLevel(logging.DEBUG)
    # root.addHandler(sh)
    # logging.getLogger("databases").setLevel(logging.ERROR)
