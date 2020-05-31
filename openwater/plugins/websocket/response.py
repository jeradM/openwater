class WebsocketResponse:
    def __init__(self, type: str):
        self.type = type

    def to_dict(self):
        return {"type": self.type, "data": self.data}

    @property
    def data(self):
        raise NotImplementedError


class ZonesResponse(WebsocketResponse):
    def __init__(self, zones):
        super().__init__(type="zones")
        self.zones = zones

    @property
    def data(self):
        return {"zones": self.zones}


class ZoneResponse(WebsocketResponse):
    def __init__(self, zone):
        super().__init__(type="zone")
        self.zone = zone

    @property
    def data(self):
        return {"zone": self.zone}
