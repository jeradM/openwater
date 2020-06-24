from typing import TYPE_CHECKING

from starlette import schemas

from openwater.core import OpenWater
from openwater.plugins.rest_api import plugins, program, schedule, steps, zone
from openwater.plugins.rest_api.helpers import ToDictJSONResponse, respond

if TYPE_CHECKING:
    from openwater.core import OpenWater

schema = schemas.SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "OpenWater API", "version": "0.0.1"}}
)


def init_endpoints(ow: OpenWater):
    plugins.register_endpoints(ow)
    program.register_endpoints(ow)
    schedule.register_endpoints(ow)
    steps.register_endpoints(ow)
    zone.register_endpoints(ow)
    ow.http.register_route(
        "/api/schema", openapi_schema, methods=["GET"], include_in_schema=False
    )
    ow.http.register_route("/api/core", core, methods=["GET"])


async def core(request) -> ToDictJSONResponse:
    return respond(request.app.ow)


async def openapi_schema(request):
    return schema.OpenAPIResponse(request)
