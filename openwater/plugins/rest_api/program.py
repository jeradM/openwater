from typing import TYPE_CHECKING, Callable

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from openwater.plugins.rest_api.helpers import ToDictJSONResponse, respond

if TYPE_CHECKING:
    from openwater.core import OpenWater


def register_endpoints(ow: "OpenWater") -> None:
    ow.http.register_route("/api/programs/{id:int}", get_program, methods=["GET"])
    ow.http.register_route("/api/programs/{id:int}", update_program, methods=["PUT"])
    ow.http.register_route("/api/programs", get_programs, methods=["GET"])


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
