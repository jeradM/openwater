from typing import TYPE_CHECKING

from openwater.database import model
from openwater.errors import OWError

if TYPE_CHECKING:
    from openwater.core import OpenWater


async def load_zones(ow: "OpenWater"):
    if not ow.db:
        raise OWError("OpenWater database not initialized")

    rows = await ow.db.connection.fetch_all(query=model.zone.select())
    for row in rows:
        zone = dict(row)
        zone_type = ow.zones.registry.get_zone_for_type(zone["zone_type"])
        if zone_type is None:
            continue
        z = zone_type.create(ow, zone)
        ow.zones.store.add_zone(z)


async def insert_zone(ow: "OpenWater", data: dict) -> int:
    conn = ow.db.connection
    new_id = await conn.execute(query=model.zone.insert(), values=data)
    return new_id


async def update_zone(ow: "OpenWater", data: dict):
    conn = ow.db.connection
    return await conn.execute(
        query=model.zone.update().where(model.zone.c.id == data["id"]), values=data
    )


async def delete_zone(ow: "OpenWater", id_: int):
    conn = ow.db.connection
    query = model.zone.delete().where(model.zone.c.id == id_)
    return await conn.execute(query=query)
