import datetime
import logging
import os

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

MIGRATION_CONFIG_FILE = 'alembic.ini'
SCRIPT_DIR_OPT = 'script_location'
DB_URL_OPT = 'sqlalchemy.url'

_LOGGER = logging.getLogger(__name__)


def migrate_db(oi, revision='head'):
    _LOGGER.info('Running DB migrations. This might take a while')
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    script_dir = os.path.join(cur_dir, 'migrations')
    alembic_conf = Config(os.path.join(cur_dir, MIGRATION_CONFIG_FILE))
    alembic_conf.set_main_option(SCRIPT_DIR_OPT, script_dir)
    alembic_conf.set_main_option(DB_URL_OPT, oi.config.get('db_url'))
    command.upgrade(alembic_conf, revision)
    _LOGGER.info('DB migration complete')


def generate_revision(oi, msg=None, autogenerate=True):
    if msg is None:
        msg = 'db_revision_{}'.format(datetime.datetime.now())
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    script_dir = os.path.join(cur_dir, 'migrations')
    alembic_conf = Config(os.path.join(cur_dir, MIGRATION_CONFIG_FILE))
    alembic_conf.set_main_option(SCRIPT_DIR_OPT, script_dir)
    alembic_conf.set_main_option(DB_URL_OPT, oi.config.get('db_url'))
    command.revision(message=msg, config=alembic_conf, autogenerate=autogenerate)


class OiDatabase:
    def __init__(self, oi):
        self.oi = oi
        self.engine = None
        self._session = None

    async def connect(self):
        def _connect():
            self.engine = create_engine(self.oi.config['db_url'])
            self._get_session = sessionmaker(bind=self.engine)
            self.oi.bus.fire('DB_CONNECTED')

        self.oi.add_task(_connect)

    async def get_session(self):
        def get_session():
            return self._session()

        return await self.oi.add_task(get_session())
