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
    route(get_program, "/api/programs/{id:int}", methods=["GET"])
    route(update_program, "/api/programs/{id:int}", methods=["PUT"])
    route(get_programs, "/api/programs", methods=["GET"])


async def get_program(request: Request) -> Response:
    ow: "OpenWater" = request.app.ow
    id_ = int(request.path_params["id"])
    return respond(ow.programs.store.get_program(id_))


async def update_program(request: Request) -> Response:
    pass


async def get_programs(request: Request) -> Response:
    """
    description: Get a list of all programs
    responses:
      200:
        description: A list of programs.
    """
    ow: "OpenWater" = request.app.ow
    return ToDictJSONResponse([p.to_dict() for p in ow.programs.store.programs])
