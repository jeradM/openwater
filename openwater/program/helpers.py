import logging
from typing import TYPE_CHECKING, Collection, Any

from databases.core import Transaction

from openwater.database import model
from openwater.database.model import program_step, program_step_zones
from openwater.errors import OWError
from openwater.program.model import ProgramSchedule, ProgramStep

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


async def load_schedules(ow: "OpenWater"):
    rows = await ow.db.list(model.schedule)
    for row in rows:
        data = dict(row)
        ow.programs.store.add_schedule(ProgramSchedule(**data))


async def load_programs(ow: "OpenWater"):
    print("load programs")
    if not ow.db:
        raise OWError("OpenWater database not initialized")

    schedules = [ProgramSchedule(**dict(s)) for s in await ow.db.list(model.schedule)]
    steps = [ProgramStep(**dict(s)) for s in await ow.db.list(model.program_step)]
    step_zones: Any = await ow.db.list(model.program_step_zones)
    for step in steps:
        step.zones = [
            ow.zones.store.get_zone(sz.zone_id)
            for sz in step_zones
            if sz.step_id == step.id
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
        ow.programs.store.add_program(p)
        p.schedules = [s for s in schedules if s.program_id == p.id]
        p.steps = [s for s in steps if s.program_id == p.id]


async def insert_program(ow: "OpenWater", data: dict) -> int:
    tx = await ow.db.connection.transaction()
    schedules = data.pop("schedules")
    steps = data.pop("steps")
    res = await ow.db.insert(model.program, data)

    for s in schedules:
        await insert_schedule(ow, s, res)

    for s in steps:
        if await insert_step(ow, s, res) == -1:
            await tx.rollback()
            return -1

    await tx.commit()
    return res


async def update_program(ow: "OpenWater", data: dict) -> bool:
    tx = await ow.db.connection.transaction().start()
    schedules = data.pop("schedules")
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
    conn = ow.db.connection
    query = model.program.delete().where(model.program.c.id == id_)
    return await conn.execute(query=query)


async def get_program_schedules(ow: "OpenWater", program_id: int) -> Collection[dict]:
    conn = ow.db.connection
    query = model.schedule.select().where(model.schedule.c.program_id == program_id)
    rows = await conn.fetch_all(query)
    return [dict(row) for row in rows]


async def insert_schedule(ow: "OpenWater", data: dict, program_id: int = None) -> int:
    if program_id is not None:
        data["program_id"] = program_id
    conn = ow.db.connection
    query = model.schedule.insert()
    return await conn.execute(query=query, values=data)


async def update_schedule(ow: "OpenWater", data):
    conn = ow.db.connection
    query = model.schedule.update().where(model.schedule.c.id == data["id"])
    return await conn.execute(query=query, values=data)


async def delete_schedule(ow: "OpenWater", schedule_id: int) -> int:
    conn = ow.db.connection
    query = model.schedule.delete().where(model.schedule.c.id == schedule_id)
    return await conn.execute(query=query)


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
    tx: Transaction = await ow.db.connection.transaction()
    try:
        id_ = await ow.db.insert(program_step, data)
        for zone in zones:
            await ow.db.insert(program_step_zones, {"step_id": id_, "zone_id": zone})
        await tx.commit()
    except Exception as e:
        _LOGGER.error("Error inserting step: %s", e)
        await tx.rollback()
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
    # tx: Transaction = await ow.db.connection.transaction()
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
        # await tx.commit()
        return ins_res
    except Exception as e:
        # await tx.rollback()
        return -1
