import logging
from typing import TYPE_CHECKING

from starlette.requests import Request
from starlette.responses import Response

from openwater.plugins.rest_api.helpers import ToDictJSONResponse, respond

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


def register_endpoints(ow: "OpenWater") -> None:
    ow.http.register_route("/api/steps", get_steps, methods=["GET"])


async def get_steps(request: Request) -> Response:
    ow: "OpenWater" = request.app.ow
    return respond(ow.programs.store.steps)


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
        zone = await ow.programs.store.create(data)
    except Exception as e:
        _LOGGER.error("Create zone failed validation")
        return ToDictJSONResponse(
            {"errors": e.errors, "msg": "Invalid zone data"}, status_code=400,
        )
    return respond(zone)
