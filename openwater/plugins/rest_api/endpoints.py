from typing import TYPE_CHECKING

from starlette import schemas
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from openwater.core import OpenWater
from openwater.plugins.rest_api import program, zone, schedule
from openwater.plugins.rest_api.helpers import ToDictJSONResponse, respond
from openwater.utils import plugin

if TYPE_CHECKING:
    from openwater.core import OpenWater

schema = schemas.SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "OpenWater API", "version": "0.0.1"}}
)


def init_endpoints(ow: OpenWater):
    ow.http.register_endpoint(Plugins)
    zone.register_endpoints(ow)
    program.register_endpoints(ow)
    schedule.register_endpoints(ow)
    ow.http.register_route(
        "/api/schema", openapi_schema, methods=["GET"], include_in_schema=False
    )
    ow.http.register_route("/api/core", core, methods=["GET"])


async def core(request) -> ToDictJSONResponse:
    return respond(request.app.ow)


async def openapi_schema(request):
    return schema.OpenAPIResponse(request)


class Plugins(HTTPEndpoint):
    path = "/api/plugins"

    async def get(self, request):
        """
        description: Get all loaded plugins
        responses:
          200:
            description: a list of all loaded plugins
        """
        p = await plugin.get_plugins(request.app.ow)
        return JSONResponse([v.to_dict() for v in p.values()])
