from typing import TYPE_CHECKING, Callable

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from openwater.plugins.rest_api.helpers import ToDictJSONResponse, respond

if TYPE_CHECKING:
    from openwater.core import OpenWater


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
