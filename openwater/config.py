import logging
import os

import aiofiles
import yaml

DEFAULT_CONFIG_DIR = ".openwater"
DEFAULT_CONFIG_FILE = "openwater.yaml"
DEFAULT_CONFIG = "db_url: sqlite:///{config_dir}/openwater.db\n"

_LOGGER = logging.getLogger(__name__)


async def load_config_file(ow):
    await ensure_config_file(ow)
    conf_file = os.path.join(get_default_config_dir(), DEFAULT_CONFIG_FILE)
    try:
        async with aiofiles.open(conf_file, "r") as f:
            c = await f.read()
            config = yaml.safe_load(c)
    except IOError:
        _LOGGER.error("Error reading OW config file")
        return None

    return config


def get_default_config_dir():
    return os.path.join(os.path.expanduser("~"), DEFAULT_CONFIG_DIR)


async def ensure_config_file(ow):
    config_file = os.path.join(get_default_config_dir(), DEFAULT_CONFIG_FILE)

    if not os.path.isdir(get_default_config_dir()):
        os.mkdir(get_default_config_dir())

    if os.path.isfile(config_file):
        return

    await ow.async_create_task(create_default_config, config_file)


def create_default_config(config_file):
    with open(config_file, "w") as f:
        f.write(DEFAULT_CONFIG.format(config_dir=get_default_config_dir()))
