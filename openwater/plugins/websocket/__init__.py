import json
import logging
from json import JSONDecodeError
from typing import TYPE_CHECKING, Dict, Any, List

from cerberus import Validator
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket

from openwater.constants import EVENT_ZONE_ADDED, EVENT_ZONE_UPDATED
from openwater.plugins.websocket.handlers import setup_handlers
from openwater.plugins.websocket.response import ZoneResponse, ZonesResponse
from openwater.utils.decorator import nonblocking

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)

DATA_WEBSOCKET = "WEBSOCKET"

WS_COMMAND_SCHEMA = {
    "cmd": {"type": "string", "required": True},
    "data": {"type": "dict", "allow_unknown": True},
}

ws_command_validator: Validator = Validator(WS_COMMAND_SCHEMA)


async def setup_plugin(ow: "OpenWater", config: Dict):
    ow.http.register_websocket_endpoint(Socket)
    ws = WebSocketApi(ow)
    ow.data[DATA_WEBSOCKET] = ws
    setup_handlers(ow, ws)


async def handle_ws_command(data: dict) -> dict:
    return {}


class WebSocketApi:
    def __init__(self, ow: "OpenWater"):
        self._ow: "OpenWater" = ow
        self.clients: List[WebSocket] = []
        self.setup_listeners()

    def setup_listeners(self) -> None:
        self._ow.bus.listen(EVENT_ZONE_ADDED, self._send_zone)
        self._ow.bus.listen(EVENT_ZONE_UPDATED, self._send_zone)

    async def _send_zone(self, event) -> None:
        if not self.clients:
            return
        zone = event.data
        resp = ZoneResponse(zone)
        for client in self.clients:
            await client.send_json(resp.to_dict())

    @nonblocking
    def send(self, type: str, data: Any, connection: WebSocket = None):
        if not self.clients:
            return
        msg = {"type": type, "data": data}
        if connection:
            self._ow.add_job(connection.send_json, msg)
        else:
            for client in self.clients:
                self._ow.add_job(client.send_json, msg)

    def add_client(self, ws: WebSocket):
        self.clients.append(ws)

    def remove_client(self, ws: WebSocket):
        self.clients.remove(ws)


class Socket(WebSocketEndpoint):
    path = "/ws"

    async def on_connect(self, websocket: WebSocket) -> None:
        ow: "OpenWater" = websocket.app.ow
        await websocket.accept()
        zones = [zone.to_dict() for zone in ow.zones.store.zones]
        await websocket.send_json(ZonesResponse(zones).to_dict())
        ws: WebSocketApi = websocket.app.ow.data[DATA_WEBSOCKET]
        ws.add_client(websocket)

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        ws: WebSocketApi = websocket.app.ow.data[DATA_WEBSOCKET]
        ws.remove_client(websocket)

    async def on_receive(self, websocket: WebSocket, data: Any) -> None:
        data_ = {}
        try:
            data_ = json.loads(data)
            valid = ws_command_validator.validate(data_)
        except JSONDecodeError:
            _LOGGER.error("WS received invalid JSON string")
            valid = False

        if not valid:
            await websocket.send_json(
                {"success": False, "errors": ws_command_validator.errors}
            )
            return

        result: dict = await handle_ws_command(data_)
        await websocket.send_json(result)