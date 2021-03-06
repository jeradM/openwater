import logging
from datetime import datetime
from logging import LogRecord
from typing import TYPE_CHECKING, List, Optional, Mapping, Any

from databases import Database
from sqlalchemy import select

from openwater.database.model import DBModel, log_entry

if TYPE_CHECKING:
    from openwater.core import OpenWater

MIGRATION_CONFIG_FILE = "alembic.ini"
SCRIPT_DIR_OPT = "script_location"
DB_URL_OPT = "sqlalchemy.url"

_LOGGER = logging.getLogger(__name__)


class OWDatabase:
    def __init__(self, ow: "OpenWater"):
        self.ow = ow
        self._database = Database(ow.config.get("db_url"))

    async def connect(self):
        await self._database.connect()
        self.ow.bus.fire("DB_CONNECTED")

    async def disconnect(self):
        await self._database.disconnect()
        self.ow.bus.fire("DB_DISCONNECTED")

    async def list(
        self, table: DBModel, order_by: Any = None, limit: int = None
    ) -> List[Mapping]:
        """
        Get a list of records from provided table
        :param table: the target model table
        :param order_by: SqlAlchemy order_by operation
        :param limit: max records to return
        :return: a list of records
        """
        query = select([table])
        if order_by is not None:
            query = query.order_by(order_by)
        if limit is not None and limit > 0:
            query = query.limit(limit)
        return await self.connection.fetch_all(query=query)

    async def get(self, table: DBModel, id_: int) -> Optional[Mapping]:
        """
        Get a single record by id from the provided table
        :param table: the target model table
        :param id_: the record id to fetch
        :return: the given record or None
        """
        query = select([table]).where(table.c.id == id_)
        return await self.connection.fetch_one(query=query)

    async def insert(self, table: DBModel, data: dict) -> int:
        """
        Insert a record into the provided table and return the new id
        :param table: the target model table
        :param data: the values to insert
        :return: the id of the new record if successful, otherwise -1
        """
        try:
            return await self.connection.execute(query=table.insert(), values=data)
        except Exception:
            return 0

    async def update(self, table: DBModel, data: dict) -> bool:
        """
        Update a database record in the provided table
        :param table: the target model table
        :param data: the values to update
        :return: True if successful, otherwise False
        """
        query = table.update().where(table.c.id == data["id"])
        res = await self.connection.execute(query=query, values=data)
        return res != 0

    async def delete(self, table: DBModel, id_: int) -> bool:
        """
        Delete the record with the provided id from the provided table
        :param table: the target model table
        :param id_: the record id to delete
        :return: True is successful, otherwise False
        """
        try:
            query = table.delete().where(table.c.id == id_)
            res = await self.connection.execute(query=query)
            return res != 0
        except Exception:
            return False

    async def delete_many(self, table: DBModel, where: Any) -> int:
        """
        Delete from table with a where clause
        :param table: the target table
        :param where: the condition
        :return: Num row deleted, or -1 if an error occurs
        """
        try:
            query = table.delete.where(where)
            res = await self.connection.execute(query=query)
            return res
        except Exception as e:
            _LOGGER.error(e)
            return -1

    @property
    def connection(self) -> Database:
        return self._database


class DatabaseLoggingHandler(logging.Handler):
    def __init__(self, ow: "OpenWater", level=logging.NOTSET):
        super().__init__(level=level)
        self._ow: "OpenWater" = ow

    def emit(self, record: LogRecord) -> None:
        row = {
            "timestamp": datetime.fromtimestamp(record.created),
            "logger": record.name,
            "level": record.levelname,
            "msg": record.msg % record.args,
        }
        self._ow.add_job(self._ow.db.insert(log_entry, row))
