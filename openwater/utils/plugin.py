import asyncio
import importlib
import logging
import os
from typing import TYPE_CHECKING, List, Dict

import yaml

from openwater.constants import EVENT_PLUGIN_LOADED
from openwater.database.model import plugin_config
from openwater.errors import PluginException

if TYPE_CHECKING:
    from openwater.core import OpenWater

PLUGIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "plugins")
PLUGIN_PKG = "openwater.plugins"
CUSTOM_PLUGIN_DIR = "custom_plugins"
CUSTOM_PLUGIN_PKG = "custom_plugins"
PLUGIN_FILENAME = "plugin.yaml"

_LOGGER = logging.getLogger(__name__)


class PluginRegistry:
    def __init__(self):
        self.all: Dict[str, "OWPlugin"] = {}
        self.enabled: Dict[str, Dict] = {}

    def enable_plugin(self, id_: str, config: Dict) -> None:
        if id_ in self.enabled:
            raise PluginException("Plugin already enabled: {}".format(id_))

        self.enabled[id_] = config

    def disable_plugin(self, id_: str) -> None:
        try:
            self.enabled.pop(id_)
        except KeyError:
            raise PluginException(
                "Attempted to disable plugin that was not enabled: {}".format(id_)
            )

    def get_config(self, id_: str) -> Dict:
        if id_ not in self.enabled:
            raise PluginException(
                "Cannot retrieve config for plugin {}: Plugin not enabled".format(id_)
            )
        return self.enabled[id_]


class OWPlugin:
    def __init__(
        self,
        id_: str,
        name: str,
        description: str,
        path: str,
        depends: List[str],
        pkg_path: str,
        core: bool = False,
        user: bool = True,
    ):
        self.id = id_
        self.name = name
        self.description = description
        self.path = path
        self.depends = depends
        self.core = core
        self.user = user
        self.pkg_path = pkg_path

    def to_dict(self):
        return self.__dict__


def plugin_from_manifest(path, pkg_name, mfst, custom=False):
    id = mfst["id"]
    name = mfst["name"]
    description = mfst["description"]
    depends = mfst.get("depends", [])
    pkg_path = "{}.{}".format(CUSTOM_PLUGIN_PKG if custom else PLUGIN_PKG, pkg_name)
    core = False if custom else (mfst.get("core", False))
    user = mfst.get("user", False)
    return OWPlugin(
        id_=id,
        name=name,
        description=description,
        path=path,
        depends=depends,
        pkg_path=pkg_path,
        core=core,
        user=user,
    )


async def get_plugins(
    ow: "OpenWater", force_rescan: bool = False
) -> Dict[str, OWPlugin]:
    if ow.plugins.all and not force_rescan:
        return ow.plugins.all

    def scan_plugins():
        plugin_defs = []
        for path, dirs, files in os.walk(PLUGIN_DIR):
            if PLUGIN_FILENAME in files:
                file_path = os.path.join(path, PLUGIN_FILENAME)
                path_parts = path.split("/")
                pkg_name = path_parts[-1]
                with open(file_path, encoding="UTF-8") as module_file:
                    p = yaml.safe_load(module_file)
                    plugin_defs.append(plugin_from_manifest(path, pkg_name, p))
        return plugin_defs

    res = await ow.add_job(scan_plugins)
    plugins = {p.id: p for p in res}
    ow.plugins.all = plugins
    return plugins


async def load_plugins(plugins: List[str], ow) -> None:
    for plugin in plugins:
        await load_plugin(plugin, ow)


async def load_plugin(id_: str, ow: "OpenWater"):
    conn = ow.db.connection
    pc = await conn.fetch_one(
        plugin_config.select().where(plugin_config.c.plugin_id == id_)
    )
    file_config = ow.config.get("plugins", {}).get(id_, {})
    if pc is None:
        config = file_config
    else:
        config = dict(pc["config"], **file_config)
    reg = ow.plugins
    if id_ not in reg.all:
        _LOGGER.error("Unable to find plugin: %s", id_)
        raise PluginException("Unable to find plugin: {}".format(id_))
    p = reg.all.get(id_)
    plugin = importlib.import_module(p.pkg_path)
    if not hasattr(plugin, "setup_plugin"):
        _LOGGER.error("Unable to load plugin %s: Missing setup_plugin function", id_)
        return
    if asyncio.coroutines.iscoroutinefunction(plugin.setup_plugin):
        await plugin.setup_plugin(ow, config)
    else:
        plugin.setup_plugin(ow, config)
    ow.bus.fire(EVENT_PLUGIN_LOADED, {"plugin": p})


async def load_logging_plugin(ow) -> None:
    await load_plugin("logger", ow)
