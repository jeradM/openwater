import importlib
import logging
import os

import asyncio
import yaml
from typing import List, Dict

PLUGIN_DIR = 'plugins'
PLUGIN_PKG = 'openirrigation.plugins'
CUSTOM_PLUGIN_DIR = 'custom_plugins'
CUSTOM_PLUGIN_PKG = 'custom_plugins'
PLUGIN_FILENAME = 'plugin.yaml'

_LOGGER = logging.getLogger(__name__)


class OiPlugin:
    def __init__(self, id: str, name: str, description: str, path: str, depends: List[str], pkg_path: str, core: bool = False):
        self.id = id
        self.name = name
        self.description = description
        self.path = path
        self.depends = depends
        self.core = core
        self.pkg_path = pkg_path

    def to_dict(self):
        return self.__dict__


def plugin_from_manifest(path, pkg_name, mfst, custom=False):
    id = mfst['id']
    name = mfst['name']
    description = mfst['description']
    depends = mfst.get('depends', [])
    pkg_path = '{}.{}'.format(CUSTOM_PLUGIN_PKG if custom else PLUGIN_PKG, pkg_name)
    core = False if custom else (mfst.get('core', False))
    return OiPlugin(id=id, name=name, description=description, path=path, depends=depends, pkg_path=pkg_path, core=core)


async def get_plugins(oi) -> Dict[str, OiPlugin]:
    if oi.plugins:
        return oi.plugins

    def scan_plugins():
        plugin_defs = []
        for path, dirs, files in os.walk(PLUGIN_DIR):
            if PLUGIN_FILENAME in files:
                file_path = os.path.join(path, PLUGIN_FILENAME)
                path_parts = path.split('/')
                pkg_name = path_parts[0] if len(path_parts) > 2 else '.'.join(path_parts[1:])
                with open(file_path, encoding='UTF-8') as module_file:
                    p = yaml.safe_load(module_file)
                    plugin_defs.append(plugin_from_manifest(path, pkg_name, p))
        return plugin_defs

    job = oi.event_loop.run_in_executor(None, scan_plugins)
    complete, _ = await asyncio.wait([job])
    res = complete.pop().result()
    plugins = {p.id: p for p in res}
    oi.plugins = plugins
    return plugins


async def load_plugins(plugins: List[str], oi) -> None:
    _plugins = ['openirrigation.plugins.{}'.format(p) for p in plugins]
    for p in _plugins:
        plugin = importlib.import_module(p)
        await plugin.setup_plugin(oi)
    print(plugins)


async def load_plugin(module_path: str, oi):
    plugin = importlib.import_module(module_path)
    if not hasattr(plugin, 'setup_plugin'):
        print('Unable to load plugin: {}'.format(module_path))
        return
    await plugin.setup_plugin(oi)


async def load_logging_plugin(oi) -> None:
    logging_path = 'openirrigation.plugins.logger'
    await load_plugin(logging_path, oi)
