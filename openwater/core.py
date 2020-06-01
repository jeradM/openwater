import asyncio
import functools
import logging
import signal
from asyncio import AbstractEventLoop
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from typing import List, Callable, Dict, Optional, Union, Any, Awaitable

from openwater.constants import (
    STATUS_STARTING,
    STATUS_RUNNING,
    EVENT_APP_STARTED,
    EVENT_TIMER_TICK_SEC,
    EVENT_TIMER_TICK_MIN,
)
from openwater.database import OWDatabase
from openwater.ow_http import OWHttp
from openwater.plugins.gpio import OWGpio
from openwater.program import BaseProgram, ProgramManager
from openwater.scheduler import Scheduler
from openwater.utils.decorator import is_blocking, is_nonblocking, nonblocking
from openwater.utils.plugin import OWPlugin, PluginRegistry
from openwater.zone import ZoneController, ZoneManager

_LOGGER = logging.getLogger(__name__)


class OpenWater:
    def __init__(self) -> None:
        self.data: dict = {}
        self.config: Optional[Dict] = None
        self.event_loop: AbstractEventLoop = asyncio.get_event_loop()
        self.executor = ThreadPoolExecutor()
        self.bus: EventBus = EventBus(self)
        self.timer = Timer(self)
        self.db: "OWDatabase" = None

        self.zones = ZoneManager(self)
        self.programs = ProgramManager(self)

        self.scheduler = Scheduler(self)
        self.plugins_: Dict[str, OWPlugin] = {}
        self.plugins = PluginRegistry()

        self.http: Optional["OWHttp"] = None
        self.gpio: Optional["OWGpio"] = None
        self._stopped = None

        self.status = STATUS_STARTING

    def add_job_ext(self, c: Union[Callable, Awaitable], *args: Any) -> None:
        self.event_loop.call_soon_threadsafe(c, *args)

    def add_job(
        self, c: Union[Callable, Awaitable], *args: Any
    ) -> Optional[asyncio.Future]:
        target = c
        while isinstance(target, functools.partial):
            target = target.func

        task = None
        if asyncio.iscoroutine(target):
            task = asyncio.create_task(c)
        elif asyncio.iscoroutinefunction(target):
            task = asyncio.create_task(c(*args))
        elif is_nonblocking(target):
            self.event_loop.call_soon(c, *args)
        else:
            task = self.event_loop.run_in_executor(None, c, *args)

        return task

    async def start(self) -> int:
        _LOGGER.info("Starting Open Irrigation")
        self._stopped = asyncio.Event()
        self.add_job(self.http.run())

        self.status = STATUS_RUNNING
        self.bus.fire(EVENT_APP_STARTED)

        await self._stopped.wait()
        return 0

    @nonblocking
    def stop(self) -> None:
        self.event_loop.remove_signal_handler(signal.SIGTERM)
        self.event_loop.remove_signal_handler(signal.SIGINT)
        self._stopped.set()


class Event:
    def __init__(
        self, ow: OpenWater, event_type: str, data: Optional[Dict], t: datetime
    ):
        self.ow = ow
        self.event_type = event_type
        self.data = data
        self.fired_at = t


class EventBus:
    def __init__(self, ow: OpenWater):
        self.ow = ow
        self._listeners: Dict[str, List] = {}

    def listen_ext(self, event_type: str, func: Callable[[Event], Any]) -> None:
        self.ow.event_loop.call_soon_threadsafe(self.listen, event_type, func)

    def listen(
        self, event_type: str, callback_: Callable[[Event], Any]
    ) -> Callable[[], None]:
        """ Add listener for this event type """

        def stop_listening():
            self.remove_listener(event_type, callback_)

        if event_type in self._listeners:
            self._listeners[event_type].append(callback_)
        else:
            self._listeners[event_type] = [callback_]

        return stop_listening

    def listen_once(self, event: str, callback: Callable[[Event], Any]) -> None:
        def listener_wrapper(evt: Event) -> None:
            self.remove_listener(event, listener_wrapper)
            self.ow.add_job(callback, evt)

        self.listen(event, listener_wrapper)

    def remove_listener(self, event: str, listener: Callable):
        try:
            self._listeners[event].remove(listener)
        except (KeyError, ValueError):
            _LOGGER.debug("Unable to remove listener")

    def fire_ext(self, event: str, data: Optional[Dict] = None) -> None:
        self.ow.event_loop.call_soon_threadsafe(self.fire, data)

    def fire(self, event: str, data: Optional[Dict] = None) -> None:
        """ Fire event (call all listeners) """
        if event not in self._listeners:
            return

        evt = Event(self.ow, event, data, datetime.now())

        for listener in self._listeners.get(event):
            self.ow.add_job(listener, event)


class Timer:
    def __init__(self, ow: OpenWater):
        self._ow = ow
        self._ow.bus.listen_once(EVENT_APP_STARTED, self.run)

    def second_tick(self, now: datetime) -> None:
        self._ow.bus.fire(EVENT_TIMER_TICK_SEC, {"now": now})

    def minute_tick(self, now: datetime) -> None:
        self._ow.bus.fire(EVENT_TIMER_TICK_MIN, {"now": now})

    @nonblocking
    def run(self, _: Event) -> None:
        async def _run():
            while True:
                now = datetime.now()
                secs = now.microsecond / 10 ** 6
                await asyncio.sleep(1 - secs)
                now = datetime.now()
                self.second_tick(now)
                if now.second == 0:
                    self.minute_tick(now)

        self._ow.add_job(_run)
