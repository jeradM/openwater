from typing import TYPE_CHECKING

from openwater.constants import EVENT_ZONE_STATE
from openwater.plugins.websocket.response import ZonesResponse
from openwater.utils.decorator import nonblocking

if TYPE_CHECKING:
    from openwater.core import OpenWater, Event
    from openwater.plugins.websocket import WebSocketApi


@nonblocking
def setup_handlers(ow: "OpenWater", ws: "WebSocketApi"):
    handler = WSEventHandler(ow, ws)
    ow.bus.listen(EVENT_ZONE_STATE, handler.zone_state)


class WSEventHandler:
    def __init__(self, ow: "OpenWater", ws: "WebSocketApi"):
        self._ow = ow
        self.ws = ws

    @nonblocking
    def zone_state(self, event: "Event"):
        self.ws.respond(ZonesResponse(self._ow.zones.store.zones))

    @nonblocking
    def zone_changed(self, event: "Event"):
        zone = event.data
        self.ws.send("ZONE_CHANGED", zone)

    @nonblocking
    def zone_deleted(self, event: "Event"):
        self.ws.send("ZONE_DELETED", event.data)
