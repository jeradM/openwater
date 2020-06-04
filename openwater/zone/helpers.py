from typing import TYPE_CHECKING, Optional

from sqlalchemy import desc, select

from openwater.database.model import zone, zone_run
from openwater.errors import OWError
from openwater.zone.model import ZoneRun

if TYPE_CHECKING:
    from openwater.core import OpenWater


async def load_zones(ow: "OpenWater"):
    if not ow.db:
        raise OWError("OpenWater database not initialized")

    rows = await ow.db.connection.fetch_all(query=zone.select())
    for row in rows:
        zone_ = dict(row)
        zone_type = ow.zones.registry.get_zone_for_type(zone_["zone_type"])
        if zone_type is None:
            continue
        z = zone_type.create(ow, zone_)
        z.last_run = await load_last_run(ow, z.id)
        ow.zones.store.add_zone(z)


async def load_last_run(ow: "OpenWater", zone_id: int) -> Optional[ZoneRun]:
    res = await ow.db.connection.fetch_one(
        query=select([zone_run])
        .where(zone_run.c.zone_id == zone_id)
        .order_by(desc(zone_run.c.start))
    )
    return ZoneRun(**res) if res else None


async def insert_zone(ow: "OpenWater", data: dict) -> int:
    conn = ow.db.connection
    new_id = await conn.execute(query=zone.insert(), values=data)
    return new_id


async def update_zone(ow: "OpenWater", data: dict):
    conn = ow.db.connection
    return await conn.execute(
        query=zone.update().where(zone.c.id == data["id"]), values=data
    )


async def delete_zone(ow: "OpenWater", id_: int):
    conn = ow.db.connection
    query = zone.delete().where(zone.c.id == id_)
    return await conn.execute(query=query)
