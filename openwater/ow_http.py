import logging
from typing import TYPE_CHECKING, Callable, Type

from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint, WebSocketEndpoint
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from uvicorn import Server, Config

from openwater.utils.decorator import nonblocking

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


async def setup_http(ow: "OpenWater"):
    middleware = [Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])]
    app = Starlette(on_shutdown=[ow.stop], middleware=middleware)
    setattr(app, "ow", ow)
    config = Config(app, host="0.0.0.0")
    ow.http = OWHttp(config)


class OWHttp:
    def __init__(self, config: Config):
        self.config = config
        self.app: Starlette = config.app

    @nonblocking
    def register_endpoint(self, endpoint: Type[HTTPEndpoint]) -> None:
        assert hasattr(endpoint, "path"), "Endpoint must define its own path"
        self.app.add_route(getattr(endpoint, "path"), endpoint)

    @nonblocking
    def register_websocket_endpoint(self, endpoint: Type[WebSocketEndpoint]):
        assert hasattr(endpoint, "path"), "Endpoint must define its own path"
        self.app.add_websocket_route(getattr(endpoint, "path"), endpoint)

    @nonblocking
    def register_route(self, endpoint: Callable, path: str, **kwargs) -> None:
        self.app.add_route(path, endpoint, **kwargs)

    @nonblocking
    def register_websocket_route(self, endpoint: Callable, path: str, **kwargs) -> None:
        self.app.add_websocket_route(path, endpoint, **kwargs)

    async def run(self):
        _LOGGER.info("Starting OpenWater HTTP server")
        server = Server(self.config)
        await server.serve()
