import sys

from cerberus import Validator
from starlette.endpoints import HTTPEndpoint
from typing import TYPE_CHECKING

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from openwater.errors import ZoneException
from openwater.zone import BaseZone

if TYPE_CHECKING:
    from openwater.core import OpenWater


ZONE_SCHEMA = {
    "id": {"type": "integer"},
    "name": {"type": "string", "maxlength": 100, "required": True},
    "active": {"type": "boolean", "required": True},
    "zone_type": {"type": "string", "maxlength": 50, "required": True},
    "attrs": {"type": "dict", "allow_unknown": True, "required": True},
}

zone_validator: Validator = Validator(ZONE_SCHEMA)


async def create_zone(request: Request):
    ow: "OpenWater" = request.app.ow
    json = await request.json()
    valid = zone_validator.validate(json)
    if not valid:
        return JSONResponse(
            {"errors": zone_validator.errors, "msg": "Invalid zone data"},
            status_code=400,
        )
    zone = await ow.zone_controller.create_zone(json)
    return JSONResponse(zone.to_dict())


async def zone_cmd(request: Request):
    ow: "OpenWater" = request.app.ow
    zone_id = request.path_params["zone_id"]
    cmd = request.path_params["cmd"]
    try:
        if cmd == "on":
            await ow.zone_controller.open_zone(zone_id)
        elif cmd == "off":
            await ow.zone_controller.close_zone(zone_id)
        else:
            raise ZoneException("Unknown zone command: {}".format(cmd))
        return JSONResponse(status_code=200)
    except Exception as e:
        print(sys.exc_info())
        return JSONResponse(status_code=500)


class Zone(HTTPEndpoint):
    path = "/api/zone/{zone_id:int}"

    async def get(self, request: Request):
        ow: "OpenWater" = request.app.ow
        zone = ow.zone_controller.get_zone_by_id(request.path_params["zone_id"])
        return JSONResponse(zone.to_dict())

    async def put(self, request):
        ow: "OpenWater" = request.app.ow
        json = await request.json()
        valid = zone_validator.validate(json)
        if not valid:
            return JSONResponse(
                {"errors": zone_validator.errors, "msg": "Invalid zone data"},
                status_code=400,
            )
        zone = await ow.zone_controller.update_zone(json)
        return JSONResponse(zone.to_dict())
