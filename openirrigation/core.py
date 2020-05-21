import asyncio
import functools
import logging
import signal
from asyncio import AbstractEventLoop
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from typing import TYPE_CHECKING, List, Callable, Dict, Optional, Union, Any, Type, Set, Iterable

from openirrigation.constants import STATUS_STARTING, STATUS_RUNNING, EVENT_APP_STARTED, \
    EVENT_TIMER_TICK_SEC, EVENT_TIMER_TICK_MIN
from openirrigation.errors import ZoneRegistrationException
from openirrigation.model import BaseZone, BaseProgram

if TYPE_CHECKING:
    from openirrigation.utils.plugin_loader import OiPlugin
    from openirrigation.plugins.http import OiHttp


_LOGGER = logging.getLogger(__name__)


class OpenIrrigation:
    def __init__(self) -> None:
        self.config: Optional[Dict] = None
        self.event_loop: AbstractEventLoop = asyncio.get_event_loop()
        self.executor = ThreadPoolExecutor()
        self.bus: EventBus = EventBus(self)
        self.zone_manager = ZoneManager(self)
        self.timer = Timer(self)
        self.plugins: Dict[str, OiPlugin] = {}
        self.http: Optional[OiHttp] = None
        self.db = None
        self.programs: List[BaseProgram] = []
        self._stopped = None

        self.status = STATUS_STARTING

        self.event_loop.add_signal_handler(signal.SIGTERM, self.stop)
        self.event_loop.add_signal_handler(signal.SIGINT, self.stop)

    def add_task(self, c: Callable[..., Any], *args: Any) -> Optional[asyncio.Future]:
        target = c
        while isinstance(target, functools.partial):
            target = target.func

        if asyncio.iscoroutine(target):
            task = self.event_loop.create_task(c)
        elif asyncio.iscoroutinefunction(target):
            task = self.event_loop.create_task(c(*args))
        else:
            task = self.event_loop.run_in_executor(self.executor, c, *args)

        return task

    async def start(self) -> int:
        _LOGGER.info('Starting Open Irrigation')
        self._stopped = asyncio.Event()
        http_task = self.add_task(self.http.run)
        self.status = STATUS_RUNNING
        self.bus.fire(EVENT_APP_STARTED)
        await self._stopped.wait()
        http_task.cancel()
        return 1

    def stop(self) -> None:
        print('Stopping')
        self.event_loop.remove_signal_handler(signal.SIGTERM)
        self.event_loop.remove_signal_handler(signal.SIGINT)
        self._stopped.set()


class Event:
    def __init__(self, oi: OpenIrrigation, event_type: str, data: Optional[Dict], t: datetime):
        self.oi = oi
        self.event_type = event_type
        self.data = data
        self.fired_at = t


class EventBus:
    def __init__(self, oi: OpenIrrigation):
        self.oi = oi
        self._listeners: Dict[str, List] = {}

    def listen(self, event: str, callback: Callable[[Event], Any]) -> Callable[[], None]:
        """ Add listener for this event type """

        def stop_listening():
            self.remove_listener(event, callback)

        if event in self._listeners:
            self._listeners[event].append(callback)
        else:
            self._listeners[event] = [callback]

        return stop_listening

    def listen_once(self, event: str, callback: Callable[[Event], Any]) -> None:
        def listener_wrapper(evt: Event) -> None:
            self.remove_listener(event, listener_wrapper)
            self.oi.add_task(callback, evt)

        self.listen(event, listener_wrapper)

    def remove_listener(self, event: str, listener: Callable):
        try:
            self._listeners[event].remove(listener)
        except (KeyError, ValueError):
            print('Unable to remove listener')

    def fire(self, event: Union[List[str], str], data: Optional[Dict] = None) -> None:
        """ Fire event (call all listeners) """
        if isinstance(event, list):
            for e in event:
                self._fire(e, data)
        else:
            self._fire(event, data)

    def _fire(self, event: str, data: Optional[Dict]) -> None:
        if event not in self._listeners:
            return

        for l in self._listeners.get(event):
            self.oi.add_task(l, Event(self.oi, event, data, datetime.now()))


class Timer:
    def __init__(self, oi: OpenIrrigation):
        self._oi = oi
        self._oi.bus.listen_once(EVENT_APP_STARTED, self.run)

    def second_tick(self, now: datetime) -> None:
        self._oi.bus.fire(EVENT_TIMER_TICK_SEC, {'now': now})

    def minute_tick(self, now: datetime) -> None:
        self._oi.bus.fire(EVENT_TIMER_TICK_MIN, {'now': now})

    def run(self, _: Event) -> None:
        async def _run():
            while True:
                now = datetime.now()
                secs = now.microsecond / 10**6
                await asyncio.sleep(1 - secs)
                now = datetime.now()
                self.second_tick(now)
                if now.second == 0:
                    self.minute_tick(now)
        self._oi.add_task(_run)


class ZoneManager:
    def __init__(self, oi: OpenIrrigation, zones: Iterable[BaseZone] = ()):
        self._oi = oi
        self.zone_types: Dict[str, Type[BaseZone]] = {}
        self.zones: Set[BaseZone] = set(zones)

    def get_zone_by_id(self, zone_id: int):
        zone = next((z for z in self.zones if z.zone_id == zone_id), None)
        if zone is None:
            _LOGGER.debug('Zone not found: {}'.format(zone_id))
        return zone

    async def open_master_zone(self):
        pass

    async def close_master_zone(self):
        pass

    async def close_zones(self, zone_ids: Iterable[int]):
        zones = (z for z in self.zones if z.zone_id in zone_ids)
        for zone in zones:
            await self._oi.add_task(zone.turn_off)

    def register_zone_type(self, zone_type: str, cls: Type[BaseZone]) -> None:
        if zone_type in self.zone_types:
            _LOGGER.error('Attempting to register duplicate zone type: {}'.format(zone_type))
            raise ZoneRegistrationException('Zone type \'{}\' has already been registered'.format(zone_type))

        self.zone_types[zone_type] = cls
        _LOGGER.debug('Registered zone type {}'.format(zone_type))

    def unregister_zone_type(self, zone_type) -> None:
        if zone_type in self.zone_types:
            self.zone_types.pop(zone_type)
            _LOGGER.debug('Unregistered zone type: {}'.format(zone_type))

    def get_zone_for_type(self, zone_type: str) -> Optional[Type[BaseZone]]:
        if zone_type not in self.zone_types:
            _LOGGER.error('Zone type not found: {}'.format(zone_type))
            return None

        return self.zone_types[zone_type]

    def get_all_registered_types(self) -> List[str]:
        return list(self.zone_types.keys())
