from typing import TYPE_CHECKING

from openwater.constants import (
    EVENT_ZONE_STATE,
    EVENT_PROGRAM_STATE,
    EVENT_SCHEDULE_STATE,
)
from openwater.plugins.websocket.response import (
    ZonesResponse,
    ProgramsResponse,
    SchedulesResponse,
)
from openwater.utils.decorator import nonblocking

if TYPE_CHECKING:
    from openwater.core import OpenWater, Event
    from openwater.plugins.websocket import WebSocketApi


@nonblocking
def setup_handlers(ow: "OpenWater", ws: "WebSocketApi"):
    handler = WSEventHandler(ow, ws)
    ow.bus.listen(EVENT_ZONE_STATE, handler.zone_state)
    ow.bus.listen(EVENT_PROGRAM_STATE, handler.program_state)
    ow.bus.listen(EVENT_SCHEDULE_STATE, handler.schedule_state)


class WSEventHandler:
    def __init__(self, ow: "OpenWater", ws: "WebSocketApi"):
        self._ow = ow
        self.ws = ws

    @nonblocking
    def program_state(self, event: "Event") -> None:
        programs = self._ow.programs.store.all
        steps = self._ow.programs.store.steps
        self.ws.respond(ProgramsResponse(programs, steps))

    @nonblocking
    def schedule_state(self, event: "Event") -> None:
        self.ws.respond(SchedulesResponse(self._ow.schedules.store.all))

    @nonblocking
    def zone_state(self, event: "Event") -> None:
        self.ws.respond(ZonesResponse(self._ow.zones.store.all))
