import logging
import sys
from typing import TYPE_CHECKING, Callable

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request

from openwater.errors import ZoneException, ZoneValidationException
from openwater.plugins.rest_api.helpers import ToDictJSONResponse, respond

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


def register_endpoints(endpoint: Callable, route: Callable):
    endpoint(Zone)
    route(create_zone, "/api/zones", methods=["POST"])
    route(get_zones, "/api/zones", methods=["GET"])
    route(zone_cmd, "/api/zones/{zone_id:int}/{cmd:str}", methods=["POST"])


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
        return respond(zone)

    async def put(self, request):
        """Update an existing zone"""
        ow: "OpenWater" = request.app.ow
        data = await request.json()
        try:
            zone = await ow.zones.store.update_zone(data)
        except ZoneValidationException as e:
            _LOGGER.error("Zone update failed validation")
            return respond({"errors": e.errors, "msg": "Invalid zone data"}, 400)
        return respond(zone)

    async def delete(self, request):
        ow: "OpenWater" = request.app.ow
        res = await ow.zones.store.delete_zone(request.path_params["zone_id"])
        sc = 204 if res else 400
        return respond(status_code=sc)


async def get_zones(request):
    """
    description: Get a list of all zones
    responses:
      200:
        description: A list of zones.
    """
    ow: "OpenWater" = request.app.ow
    return respond(ow.zones.store.zones)


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
        return ToDictJSONResponse(
            {"errors": e.errors, "msg": "Invalid zone data"}, status_code=400,
        )
    return respond(zone)


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
        return respond(status_code=200)
    except ZoneException as e:
        _LOGGER.error(e)
        return respond(status_code=500)
