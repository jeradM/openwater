from typing import TYPE_CHECKING, Collection

from openwater.database import model
from openwater.database.model import schedule
from openwater.errors import OWError
from openwater.program.model import ProgramSchedule

if TYPE_CHECKING:
    from openwater.core import OpenWater


async def load_schedules(ow: "OpenWater"):
    rows = await ow.db.list(schedule)
    for row in rows:
        data = dict(row)
        ow.programs.store.add_schedule(ProgramSchedule(**data))


async def load_programs(ow: "OpenWater"):
    print("load programs")
    if not ow.db:
        raise OWError("OpenWater database not initialized")

    rows = await ow.db.connection.fetch_all(query=model.program.select())
    for row in rows:
        program = dict(row)
        program_type = ow.programs.registry.get_program_for_type(
            program["program_type"]
        )
        if program_type is None:
            continue
        p = program_type.create(ow, program)
        ow.programs.store.add_program(p)

    await load_schedules(ow)


async def insert_program(ow: "OpenWater", data: dict) -> int:
    conn = ow.db.connection
    return await conn.execute(query=model.program.insert(), values=data)


async def update_program(ow: "OpenWater", data: dict) -> int:
    conn = ow.db.connection
    query = model.program.update().where(model.program.c.id == data["id"])
    return await conn.execute(query=query, values=data)


async def delete_program(ow: "OpenWater", id_: int) -> int:
    conn = ow.db.connection
    query = model.program.delete().where(model.program.c.id == id_)
    return await conn.execute(query=query)


async def get_program_schedules(ow: "OpenWater", program_id: int) -> Collection[dict]:
    conn = ow.db.connection
    query = model.schedule.select().where(model.schedule.c.program_id == program_id)
    rows = await conn.fetch_all(query)
    return [dict(row) for row in rows]


async def insert_schedule(ow: "OpenWater", data: dict) -> int:
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
