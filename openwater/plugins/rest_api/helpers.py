import datetime
import json
from typing import Any

from starlette.responses import JSONResponse

from openwater.utils.decorator import nonblocking


@nonblocking
def respond(data=None, status_code=200):
    return ToDictJSONResponse(content=data, status_code=status_code)


class ToDictJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        try:
            if isinstance(o, list):
                return [i.to_dict for i in o]
            if isinstance(o, datetime.date):
                return str(o)
            return o.to_dict()
        except AttributeError:
            return json.JSONEncoder.default(self, o)


class ToDictJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=ToDictJSONEncoder,
        ).encode("utf-8")
