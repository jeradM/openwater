import logging
from typing import Callable, Optional, Type

from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.routing import Route, Mount
from uvicorn import Server, Config

_LOGGER = logging.getLogger(__name__)


async def setup_plugin(oi):
    app = Starlette()
    setattr(app, 'oi', oi)
    config = Config(app)
    oi.http = OiHttp(config)


class OiHttp:
    def __init__(self, config: Config):
        self.config = config
        self.app = config.app

    def register_new_endpoint(self, endpoint: Type[HTTPEndpoint]) -> None:
        assert hasattr(endpoint, 'path'), 'Endpoint must define its own path'
        self.app.add_route(getattr(endpoint, 'path'), endpoint)

    def register_endpoint(self, url: str, endpoint: Callable, base: Optional[str] = None) -> None:
        if base is not None:
            bases = base.split('/')
            mount = None
            for b in bases:
                if b == '':
                    continue
                _base = '/{}'.format(b)
                _mount = Mount(path=_base, routes=[])
                _routes = self.app.routes if mount is None else mount.routes
                mounts = [m for m in _routes if m.path == _base and isinstance(m, Mount)]
                if len(mounts) > 0:
                    mount = mounts[0]
                else:
                    _routes.append(_mount)
                    mount = _mount
            routes = mount.routes
        else:
            routes = self.app.routes

        route = Route(url, endpoint=endpoint)
        routes.append(route)

    async def run(self):
        _LOGGER.info('Starting OI HTTP server')
        server = Server(self.config)
        await server.serve()
