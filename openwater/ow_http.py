import logging
from typing import TYPE_CHECKING, Callable, Optional, Type

from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint, WebSocketEndpoint
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route, Mount
from starlette.schemas import SchemaGenerator
from uvicorn import Server, Config

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


async def setup_http(ow: "OpenWater"):
    middleware = [Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])]
    app = Starlette(on_shutdown=[ow.stop], middleware=middleware)
    setattr(app, "ow", ow)
    config = Config(app)
    ow.http = OWHttp(config)


class OWHttp:
    def __init__(self, config: Config):
        self.config = config
        self.app = config.app

    def register_endpoint(self, endpoint: Type[HTTPEndpoint]) -> None:
        assert hasattr(endpoint, "path"), "Endpoint must define its own path"
        self.app.add_route(getattr(endpoint, "path"), endpoint)

    def register_websocket_endpoint(self, endpoint: Type[WebSocketEndpoint]):
        assert hasattr(endpoint, "path"), "Endpoint must define its own path"
        self.app.add_websocket_route(getattr(endpoint, "path"), endpoint)

    def register_route(self, endpoint: Callable, path: str, **kwargs) -> None:
        self.app.add_route(path, endpoint, **kwargs)

    def register_new_endpoint(
        self, url: str, endpoint: Callable, base: Optional[str] = None
    ) -> None:
        if base is not None:
            bases = base.split("/")
            mount = None
            for b in bases:
                if b == "":
                    continue
                _base = "/{}".format(b)
                _mount = Mount(path=_base, routes=[])
                _routes = self.app.routes if mount is None else mount.routes
                mounts = [
                    m for m in _routes if m.path == _base and isinstance(m, Mount)
                ]
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
        _LOGGER.info("Starting OpenWater HTTP server")
        server = Server(self.config)
        await server.serve()
