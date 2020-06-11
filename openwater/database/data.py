import datetime
from random import choice, randint


def get_master_data():
    return {
        "name": "Master Zone 1",
        "zone_type": "SHIFT_REGISTER",
        "is_master": True,
        "open_offset": 5,
        "close_offset": 7,
        "attrs": {"sr_idx": 0},
    }


def get_zone_data():
    return [
        {
            "name": "Test Zone {}".format(i),
            "zone_type": "SHIFT_REGISTER",
            "attrs": {"sr_idx": i, "soil_type": "CLAY", "precip_rate": 0.2 + (i / 10)},
        }
        for i in range(1, 8)
    ]


def get_zone_run_data():
    now = datetime.datetime.now()
    return [
        {
            "zone_id": randint(2, 9),
            "start": now
            + datetime.timedelta(
                days=randint(-30, -1), hours=randint(-8, 8), minutes=randint(-10, 20)
            ),
            "duration": randint(300, 7200),
        }
        for i in range(100)
    ]


def get_master_zone_join_data():
    return [{"zone_id": i, "master_zone_id": 1} for i in range(2, 5)]


def get_program_data():
    return [
        {"name": "Test Program {}".format(i), "program_type": "Basic", "attrs": {}}
        for i in range(2)
    ]


def get_program_step_data():
    types = ["Sequential", "Soak"]
    return [
        {"program_id": 1, "order": i, "duration": randint(1, 5)} for i in range(1, 8)
    ]


def get_step_zones_data():
    res = []
    for i in range(1, 8):
        res.append({"zone_id": i + 1, "step_id": i})
    return res


def get_schedules_data():
    return [
        {
            "program_id": 1,
            "enabled": True,
            "at": int(6.5 * 60),
            "dow_mask": 86,
            "days_restriction": "E",
        },
        {
            "program_id": 1,
            "enabled": True,
            "at": int(14.75 * 60),
            "start_day": datetime.date(2020, 6, 5),
            "day_interval": 3,
        },
    ]
