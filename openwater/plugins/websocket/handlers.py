from typing import TYPE_CHECKING

from openwater.constants import EVENT_ZONE_CHANGED, EVENT_ZONE_DELETED
from openwater.utils.decorator import nonblocking

if TYPE_CHECKING:
    from openwater.core import OpenWater, Event
    from openwater.plugins.websocket import WebSocketApi


@nonblocking
def setup_handlers(ow: "OpenWater", ws: "WebSocketApi"):
    handler = WSEventHandler(ws)
    ow.bus.listen(EVENT_ZONE_CHANGED, handler.zone_changed)
    ow.bus.listen(EVENT_ZONE_DELETED, handler.zone_deleted)


class WSEventHandler:
    def __init__(self, ws: "WebSocketApi"):
        self.ws = ws

    @nonblocking
    def zone_changed(self, event: "Event"):
        zone = event.data
        self.ws.send("ZONE_CHANGED", zone)

    @nonblocking
    def zone_deleted(self, event: "Event"):
        self.ws.send("ZONE_DELETED", event.data)
