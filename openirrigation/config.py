import logging
import os

import aiofiles
import yaml

DEFAULT_CONFIG_DIR = '.openirrigation'
DEFAULT_CONFIG_FILE = 'openirrigation.yaml'
DEFAULT_CONFIG = 'db_url: sqlite:///{config_dir}/openirrigation.db\n'

_LOGGER = logging.getLogger(__name__)


async def load_config_file(oi):
    await ensure_config_file(oi)
    conf_file = os.path.join(get_default_config_dir(), DEFAULT_CONFIG_FILE)
    try:
        async with aiofiles.open(conf_file, 'r') as f:
            c = await f.read()
            config = yaml.safe_load(c)
    except IOError:
        _LOGGER.error('Error reading OI config file')
        return None

    return config


def get_default_config_dir():
    return os.path.join(os.path.expanduser('~'), DEFAULT_CONFIG_DIR)


async def ensure_config_file(oi):
    config_file = os.path.join(get_default_config_dir(), DEFAULT_CONFIG_FILE)

    if not os.path.isdir(get_default_config_dir()):
        os.mkdir(get_default_config_dir())

    if os.path.isfile(config_file):
        return

    await oi.add_task(create_default_config, config_file)


def create_default_config(config_file):
    with open(config_file, 'w') as f:
        f.write(DEFAULT_CONFIG.format(config_dir=get_default_config_dir()))
