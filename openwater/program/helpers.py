from typing import TYPE_CHECKING, Collection

from openwater.database import model
from openwater.errors import OWError
from openwater.program.model import ProgramSchedule

if TYPE_CHECKING:
    from openwater.core import OpenWater


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


async def insert_program(ow: "OpenWater", data: dict) -> int:
    conn = ow.db.connection
    new_id = await conn.execute(query=model.program.insert(), values=data)
    return new_id


async def update_program(ow: "OpenWater", data: dict):
    conn = ow.db.connection
    await conn.execute(query=model.program.update(), values=data)


async def delete_program(ow: "OpenWater", id_: int):
    conn = ow.db.connection
    query = model.program.delete().where(model.program.c.id == id_)
    await conn.execute(query=query)


async def get_program_schedules(
    ow: "OpenWater", program_id: int
) -> Collection[ProgramSchedule]:
    conn = ow.db.connection
    query = model.schedule.select().where(model.schedule.c.program_id == program_id)
    rows = await conn.fetch_all(query)
    return [ProgramSchedule(**(dict(row))) for row in rows]
