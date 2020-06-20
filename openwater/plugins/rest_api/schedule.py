import logging
from json.decoder import JSONDecodeError
from typing import TYPE_CHECKING

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import *

from openwater.errors import ScheduleValidationException
from openwater.plugins.rest_api.helpers import respond
from openwater.schedule.model import ScheduleType

if TYPE_CHECKING:
    from openwater.core import OpenWater

_LOGGER = logging.getLogger(__name__)


def register_endpoints(ow: "OpenWater") -> None:
    ow.http.register_endpoint(ScheduleEndpoint)
    ow.http.register_endpoint(SchedulesEndpoint)
    ow.http.register_route("/api/schedule_types", get_schedule_types, methods=["GET"])


class ScheduleEndpoint(HTTPEndpoint):
    path = "/api/schedules/{id:int}"

    async def get(self, request: Request) -> Response:
        ow: "OpenWater" = request.app.ow
        schedule = ow.schedules.store.get(request.path_params["id"])
        if not schedule:
            return respond(status_code=HTTP_404_NOT_FOUND)
        return respond(schedule)

    async def put(self, request: Request) -> Response:
        ow: "OpenWater" = request.app.ow
        data: dict = await request.json()
        try:
            status_code = HTTP_200_OK
            if not await ow.schedules.store.update(data):
                status_code = HTTP_400_BAD_REQUEST
            return respond(status_code=status_code)
        except ScheduleValidationException as e:
            return respond({"errors": e.errors}, HTTP_400_BAD_REQUEST)
        except Exception as e:
            return respond({"error": e.args[0]}, HTTP_400_BAD_REQUEST)


class SchedulesEndpoint(HTTPEndpoint):
    path = "/api/schedules"

    async def get(self, request: Request) -> Response:
        ow: "OpenWater" = request.app.ow
        return respond(ow.schedules.store.all)

    async def post(self, request: Request) -> Response:
        """
        description: Create a new schedule
        responses:
          200:
            description: Successfully created schedule
          400:
            description: Invalid data sent
        """
        ow: "OpenWater" = request.app.ow
        try:
            data = await request.json()
            zone = await ow.schedules.store.create(data)
            return respond(zone)
        except JSONDecodeError as e:
            return respond({"error": e.msg}, HTTP_400_BAD_REQUEST)
        except ScheduleValidationException as e:
            return respond({"errors": e.errors}, HTTP_400_BAD_REQUEST)


async def get_schedule_types(request: Request) -> Response:
    return respond([st.value for st in ScheduleType])


# async def get_schedules_for_program(request: Request) -> Response:
#     ow: "OpenWater" = request.app.ow
#     id_ = request.path_params["id"]
#     return respond(await ow.programs.store.get_schedules(id_))
