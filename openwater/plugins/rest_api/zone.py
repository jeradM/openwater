import json
import logging
import sys
from json import JSONEncoder

from starlette.endpoints import HTTPEndpoint
from typing import TYPE_CHECKING, Callable, Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from openwater.errors import ZoneException, ZoneValidationException
from openwater.utils.decorator import nonblocking
from openwater.zone.model import BaseZone

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


def register_zone_endpoints(endpoint: Callable, route: Callable):
    endpoint(Zone)
    route(create_zone, "/api/zones", methods=["POST"])
    route(get_zones, "/api/zones", methods=["GET"])
    route(zone_cmd, "/api/zones/{zone_id:int}/{cmd:str}", methods=["POST"])


@nonblocking
def respond(*, data=None, status_code=200):
    return JSONResponse(content=data, status_code=status_code)


class Zone(HTTPEndpoint):
    path = "/api/zones/{zone_id:int}"

    async def get(self, request: Request):
        """
        description: Get a zone by id
        parameters:
          - in: path
            name: zone_id:int
            description: Numeric id of requested zone
            required: true
            schema:
              type: integer
        responses:
          200:
            description: A zone
        """
        ow: "OpenWater" = request.app.ow
        zone = ow.zones.store.get_zone(request.path_params["zone_id"])
        return ZoneJSONResponse(zone)

    async def put(self, request):
        """Update an existing zone"""
        ow: "OpenWater" = request.app.ow
        data = await request.json()
        try:
            zone = await ow.zones.store.update_zone(data)
        except ZoneValidationException as e:
            _LOGGER.error("Zone update failed validation")
            return JSONResponse(
                {"errors": e.errors, "msg": "Invalid zone data"}, status_code=400,
            )
        return JSONResponse(zone.to_dict())

    async def delete(self, request):
        ow: "OpenWater" = request.app.ow
        await ow.zones.store.delete_zone(request.path_params["zone_id"])
        return JSONResponse(status_code=204)


async def get_zones(request):
    """
    description: Get a list of all zones
    responses:
      200:
        description: A list of zones.
    """
    ow: "OpenWater" = request.app.ow
    return ZoneJSONResponse(list(ow.zones.store.zones))


async def create_zone(request: Request):
    """
    description: Create a new zone
    responses:
      200:
        description: Successfully created zone
      400:
        description: Invalid data sent
    """
    ow: "OpenWater" = request.app.ow
    data = await request.json()
    try:
        zone = await ow.zones.store.create_zone(data)
    except ZoneValidationException as e:
        _LOGGER.error("Create zone failed validation")
        return JSONResponse(
            {"errors": e.errors, "msg": "Invalid zone data"}, status_code=400,
        )
    return ZoneJSONResponse(zone)


async def zone_cmd(request: Request):
    """
    description: Execute a zone command
    parameters:
      - in: path
        name: zone_id:int
        description: Numeric id of target zone
        required: true
        schema:
          type: integer
      - in: path
        name: cmd:str
        description: the command to execute
        required: true
        schema:
          type: string
    responses:
      200:
        description: successfully executed command
      500:
        description: unable to execute given command
    """
    ow: "OpenWater" = request.app.ow
    zone_id = request.path_params["zone_id"]
    cmd = request.path_params["cmd"]
    try:
        if cmd == "on":
            await ow.zones.controller.open_zone(zone_id)
        elif cmd == "off":
            await ow.zones.controller.close_zone(zone_id)
        else:
            raise ZoneException("Unknown zone command: {}".format(cmd))
        return JSONResponse(status_code=200)
    except Exception as e:
        print(sys.exc_info())
        return JSONResponse(status_code=500)


class ZoneEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, BaseZone):
            return o.to_dict()
        return json.JSONEncoder.default(self, o)


class ZoneJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=ZoneEncoder,
        ).encode("utf-8")
