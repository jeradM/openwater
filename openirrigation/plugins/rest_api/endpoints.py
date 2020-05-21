from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from openirrigation.core import OpenIrrigation
from openirrigation.utils import plugin_loader


def init_endpoints(oi: OpenIrrigation):
    oi.http.register_new_endpoint(Plugins)
    oi.http.register_new_endpoint(Index)


class Index(HTTPEndpoint):
    path = '/api/'

    async def get(self, request):
        return JSONResponse({'hello': 'world'})


class Plugins(HTTPEndpoint):
    path = '/api/plugins'

    async def get(self, request):
        p = await plugin_loader.get_plugins(request.app.oi)
        return JSONResponse([v.to_dict() for v in p.values()])
