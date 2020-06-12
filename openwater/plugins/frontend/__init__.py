import os
from typing import TYPE_CHECKING

from starlette.requests import Request
from starlette.responses import FileResponse

from openwater.constants import EVENT_PLUGINS_COMPLETE
from openwater.utils.decorator import nonblocking

if TYPE_CHECKING:
    from openwater.core import OpenWater, Event

STATIC_PATH = os.path.join(os.path.dirname(__file__), "dist")


async def setup_plugin(ow: "OpenWater", config: dict) -> None:
    js_dir = os.path.join(STATIC_PATH, "js")
    css_dir = os.path.join(STATIC_PATH, "css")
    ow.http.register_static_directory(path="/js", dir=js_dir)
    ow.http.register_static_directory(path="/css", dir=css_dir)

    @nonblocking
    def register_root_path(event: "Event"):
        ow.http.register_route("/{p:path}", index)

    ow.bus.listen_once(EVENT_PLUGINS_COMPLETE, register_root_path)


async def index(request: Request):
    return FileResponse(os.path.join(STATIC_PATH, "index.html"))
