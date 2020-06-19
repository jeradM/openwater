from typing import TYPE_CHECKING

from openwater.constants import EVENT_ZONE_STATE, EVENT_PROGRAM_STATE
from openwater.plugins.websocket.response import ZonesResponse, ProgramsResponse
from openwater.utils.decorator import nonblocking

if TYPE_CHECKING:
    from openwater.core import OpenWater, Event
    from openwater.plugins.websocket import WebSocketApi
    from openwater.program.model import BaseProgram


@nonblocking
def setup_handlers(ow: "OpenWater", ws: "WebSocketApi"):
    handler = WSEventHandler(ow, ws)
    ow.bus.listen(EVENT_ZONE_STATE, handler.zone_state)
    ow.bus.listen(EVENT_PROGRAM_STATE, handler.program_state)


class WSEventHandler:
    def __init__(self, ow: "OpenWater", ws: "WebSocketApi"):
        self._ow = ow
        self.ws = ws

    @nonblocking
    def program_state(self, event: "Event"):
        programs = self._ow.programs.store.programs
        schedules = self._ow.programs.store.schedules
        steps = self._ow.programs.store.steps
        self.ws.respond(ProgramsResponse(programs, schedules, steps))

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
