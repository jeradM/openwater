import logging
from typing import TYPE_CHECKING, Collection, Any

from databases.core import Transaction

from openwater.database import model
from openwater.database.model import program_step, program_step_zones
from openwater.errors import OWError
from openwater.program.model import ProgramStep

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


async def load_programs(ow: "OpenWater"):
    if not ow.db:
        raise OWError("OpenWater database not initialized")

    steps = [ProgramStep(**dict(s)) for s in await ow.db.list(model.program_step)]
    ow.programs.store.set_steps(steps)
    step_zones: Any = await ow.db.list(model.program_step_zones)
    for step in steps:
        step.zones = [
            ow.zones.store.get(sz.zone_id) for sz in step_zones if sz.step_id == step.id
        ]

    programs: Any = await ow.db.list(model.program)

    for row in programs:
        program = dict(row)
        program_type = ow.programs.registry.get_program_for_type(
            program["program_type"]
        )
        if program_type is None:
            continue
        p = program_type.create(ow, program)
        ow.programs.store.add(p)
        p.steps = [s for s in steps if s.program_id == p.id]


async def insert_program(ow: "OpenWater", data: dict) -> int:
    tx = await ow.db.connection.transaction()
    steps = data.pop("steps")
    res = await ow.db.insert(model.program, data)

    for s in steps:
        if await insert_step(ow, s, res) == -1:
            await tx.rollback()
            return 0

    await tx.commit()
    return res


async def update_program(ow: "OpenWater", data: dict) -> bool:
    tx = await ow.db.connection.transaction()
    steps = data.pop("steps")
    res = await ow.db.update(model.program, data)
    if not res:
        await tx.rollback()
        return False
    for s in steps:
        if "id" in s:
            await update_step(ow, s)
        else:
            await insert_step(ow, s, data["id"])
    await tx.commit()
    return True


async def delete_program(ow: "OpenWater", id_: int) -> int:
    return await ow.db.delete(model.program, id_)


async def get_program_schedules(ow: "OpenWater", program_id: int) -> Collection[dict]:
    conn = ow.db.connection
    query = model.schedule.select().where(model.schedule.c.program_id == program_id)
    rows = await conn.fetch_all(query)
    return [dict(row) for row in rows]


async def insert_steps(ow: "OpenWater", data: list) -> bool:
    tx: Transaction = await ow.db.connection.transaction()
    for step in data:
        res = await insert_step(ow, step)
        if res == -1:
            await tx.rollback()
            return False
    await tx.commit()
    return True


async def insert_step(ow: "OpenWater", data: dict, program_id: int = None) -> int:
    zones = data.pop("zones")
    if program_id is not None:
        data["program_id"] = program_id
    try:
        id_ = await ow.db.insert(program_step, data)
        for zone in zones:
            await ow.db.insert(program_step_zones, {"step_id": id_, "zone_id": zone})
    except Exception as e:
        _LOGGER.error("Error inserting step: %s", e)
        return -1


async def update_steps(ow: "OpenWater", data: list) -> bool:
    tx: Transaction = await ow.db.connection.transaction()
    for step in data:
        res = await update_step(ow, step)
        if res == -1:
            await tx.rollback()
            return False
    await tx.commit()
    return True


async def update_step(ow: "OpenWater", data: dict) -> int:
    zones = data.pop("zones")
    try:
        ins_res = await ow.db.update(program_step, data)
        del_res = await ow.db.delete_many(
            program_step_zones, program_step_zones.c.step_id == data["id"]
        )
        if del_res == -1:
            raise Exception("Failed to delete existing step_zones")
        for zone in zones:
            await ow.db.insert(
                program_step_zones, {"step_id": data["id"], "zone_id": zone}
            )
        return ins_res
    except Exception as e:
        _LOGGER.error(e)
        return -1
