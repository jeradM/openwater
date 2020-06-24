class WebsocketResponse:
    def __init__(self, type: str):
        self.type = type

    def to_dict(self):
        return {"type": self.type, "data": self.data}

    @property
    def data(self):
        raise NotImplementedError


class ProgramsResponse(WebsocketResponse):
    def __init__(self, programs, steps):
        super().__init__(type="state.programs")
        self.programs = programs
        self.steps = steps

    @property
    def data(self):
        return {
            "programs": self.programs,
            "steps": self.steps,
        }


class SchedulesResponse(WebsocketResponse):
    def __init__(self, schedules):
        super().__init__(type="state.schedules")
        self.schedules = schedules

    @property
    def data(self):
        return {"schedules": self.schedules}


class ZonesResponse(WebsocketResponse):
    def __init__(self, zones):
        super().__init__(type="state.zones")
        self.zones = zones

    @property
    def data(self):
        return {"zones": self.zones}
