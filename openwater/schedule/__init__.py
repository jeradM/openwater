from typing import TYPE_CHECKING

from openwater.schedule.store import ScheduleStore

if TYPE_CHECKING:
    from openwater.core import OpenWater


class ScheduleManager:
    def __init__(self, ow: "OpenWater"):
        self.store = ScheduleStore(ow)
