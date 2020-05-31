from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from openwater.core import OpenWater
from openwater.plugins.rest_api.zone import Zone, create_zone, zone_cmd
from openwater.utils import plugin

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openwater.core import OpenWater


def init_endpoints(ow: OpenWater):
    # ow.http.register_new_endpoint(Zones)
    ow.http.register_endpoint(Zone)
    ow.http.register_route(create_zone, "/api/zone", methods=["POST"])
    ow.http.register_route(zones, "/api/zones/", methods=["GET"])
    ow.http.register_route(
        zone_cmd, "/api/zone/{zone_id:int}/{cmd:str}", methods=["POST"]
    )
    ow.http.register_endpoint(Plugins)
    ow.http.register_endpoint(Index)


class Index(HTTPEndpoint):
    path = "/api/"

    async def get(self, request):
        return JSONResponse({"hello": "world"})


async def zones(request):
    ow: "OpenWater" = request.app.ow
    zones = [z.to_dict() for z in ow.zone_controller.zones.values()]
    return JSONResponse(zones)


class Zones(HTTPEndpoint):
    path = "/api/zones/"

    async def get(self, request):
        ow: "OpenWater" = request.app.ow
        zones = [z.to_dict() for z in ow.zone_controller.zones]
        return JSONResponse(zones)


class Plugins(HTTPEndpoint):
    path = "/api/plugins"

    async def get(self, request):
        p = await plugin.get_plugins(request.app.ow)
        return JSONResponse([v.to_dict() for v in p.values()])
