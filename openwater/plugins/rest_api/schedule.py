import logging
from typing import TYPE_CHECKING, Callable

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from openwater.plugins.rest_api.helpers import ToDictJSONResponse, respond

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


def register_endpoints(endpoint: Callable, route: Callable) -> None:
    """
    endpoint: OWHttp.register_endpoint
    route: OWHttp.register_route
    """
    route(
        get_schedules_for_program, "/api/programs/{id:int}/schedules", methods=["GET"]
    )


async def get_schedules_for_program(request: Request) -> Response:
    ow: "OpenWater" = request.app.ow
    id_ = request.path_params["id"]
    return respond(await ow.programs.store.get_schedules(id_))


async def create_schedule(request: Request) -> Response:
    """
    description: Create a new schedule
    responses:
      200:
        description: Successfully created schedule
      400:
        description: Invalid data sent
    """
    ow: "OpenWater" = request.app.ow
    data = await request.json()
    try:
        zone = await ow.programs.store.create_program(data)
    except Exception as e:
        _LOGGER.error("Create zone failed validation")
        return ToDictJSONResponse(
            {"errors": e.errors, "msg": "Invalid zone data"}, status_code=400,
        )
    return respond(zone)
