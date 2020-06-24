import logging
from typing import TYPE_CHECKING

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import Response

from openwater.plugins.rest_api.helpers import respond
from openwater.utils import plugin

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


def register_endpoints(ow: "OpenWater") -> None:
    ow.http.register_endpoint(PluginsEndpoint)


class PluginsEndpoint(HTTPEndpoint):
    path = "/api/plugins"

    async def get(self, request: Request) -> Response:
        """
        description: Get all loaded plugins
        responses:
          200:
            description: a list of all loaded plugins
        """
        return respond(await plugin.get_plugins(request.app.ow))
