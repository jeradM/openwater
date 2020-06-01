from typing import TYPE_CHECKING

from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from starlette import schemas

from openwater.core import OpenWater
from openwater.plugins.rest_api.zone import register_zone_endpoints
from openwater.utils import plugin

if TYPE_CHECKING:
    from openwater.core import OpenWater

schema = schemas.SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "OpenWater API", "version": "0.0.1"}}
)


def init_endpoints(ow: OpenWater):
    ow.http.register_endpoint(Plugins)
    register_zone_endpoints(ow.http.register_endpoint, ow.http.register_route)
    ow.http.register_route(
        openapi_schema, "/api/schema", methods=["GET"], include_in_schema=False
    )


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
