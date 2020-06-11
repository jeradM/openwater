import logging
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import desc, select

from openwater.database.model import zone, zone_run, master_zone_join
from openwater.errors import OWError
from openwater.zone.model import ZoneRun, BaseZone

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


async def load_zones(ow: "OpenWater"):
    if not ow.db:
        _LOGGER.error("Database not initialized")
        raise OWError("OpenWater database not initialized")

    _LOGGER.debug("Loading zones from database")
    rows = await ow.db.list(zone)
    for row in rows:
        zone_ = dict(row)
        zone_type = ow.zones.registry.get_zone_for_type(zone_["zone_type"])
        if zone_type is None:
            continue
        z = zone_type.create(ow, zone_)
        z.last_run = await load_last_run(ow, z.id)
        ow.zones.store.add_zone(z)

    _LOGGER.debug("Loaded %d zones", len(ow.zones.store.zones))

    await load_masters(ow)


async def load_masters(ow: "OpenWater") -> None:
    rows = await ow.db.list(master_zone_join)
    for row in rows:
        zone_ = ow.zones.store.get_zone(row[0])
        master_ = ow.zones.store.get_zone(row[1])
        if zone_.master_zones is None:
            zone_.master_zones = [master_]
        else:
            zone_.master_zones.append(master_)
    _LOGGER.debug("Loaded %d master zones", len(rows))


async def load_last_run(ow: "OpenWater", zone_id: int) -> Optional[ZoneRun]:
    res = await ow.db.connection.fetch_one(
        query=select([zone_run])
        .where(zone_run.c.zone_id == zone_id)
        .order_by(desc(zone_run.c.start))
    )
    return ZoneRun(**res) if res else None


async def insert_zone(ow: "OpenWater", data: dict) -> int:
    return await ow.db.insert(zone, data)


async def update_zone(ow: "OpenWater", data: dict) -> bool:
    return await ow.db.update(zone, data)


async def delete_zone(ow: "OpenWater", id_: int) -> bool:
    return await ow.db.delete(zone, id_)
