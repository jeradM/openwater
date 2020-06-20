import logging
from typing import TYPE_CHECKING, Collection, Any

from databases.core import Transaction

from openwater.database import model
from openwater.database.model import program_step, program_step_zones
from openwater.errors import OWError
from openwater.program.model import ProgramStep
from openwater.schedule.model import ProgramSchedule

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


async def load_schedules(ow: "OpenWater"):
    rows = await ow.db.list(model.schedule)
    for row in rows:
        data = dict(row)
        ow.schedules.store.add(ProgramSchedule(**data))
    _LOGGER.debug("Loaded %d schedules", len(rows))


async def insert_schedule(ow: "OpenWater", data: dict, program_id: int = None) -> int:
    if program_id is not None:
        data["program_id"] = program_id
    return await ow.db.insert(model.schedule, data)


async def update_schedule(ow: "OpenWater", data):
    return await ow.db.update(model.schedule, data)


async def delete_schedule(ow: "OpenWater", schedule_id: int) -> int:
    return await ow.db.delete(model.schedule, schedule_id)
