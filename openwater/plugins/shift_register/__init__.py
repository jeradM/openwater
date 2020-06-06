from typing import TYPE_CHECKING, Optional

from cerberus import Validator

from openwater.errors import ZoneException, ZoneValidationException
from openwater.plugins.gpio import DATA_GPIO, OWGpio
from openwater.zone.model import BaseZone

if TYPE_CHECKING:
    from openwater.core import OpenWater


DATA_SHIFT_REGISTER = "SHIFT_REGISTER"
ZONE_TYPE_SHIFT_REGISTER = "SHIFT_REGISTER"


def setup_plugin(ow: "OpenWater", config: dict = {}):
    gpio: Optional[OWGpio] = ow.data[DATA_GPIO]
    if not gpio:
        raise ZoneException("Required plugin(s) not enabled: {}", ["gpio"])

    num_reg = config.get("num_reg", 8)
    data_pin = config.get("data_pin", 0)
    clock_pin = config.get("clock_pin", 0)
    oe_pin = config.get("oe_pin", 0)
    latch_pin = config.get("latch_pin", 0)
    if not (data_pin and clock_pin and oe_pin and latch_pin):
        raise ZoneException("Must define all required shift register pins")

    gpio.set_output([data_pin, clock_pin, oe_pin, latch_pin])
    active_high = config.get("active_high", True)
    sr = ShiftRegister(
        ow, gpio, data_pin, clock_pin, oe_pin, latch_pin, num_reg, active_high
    )
    ow.data[DATA_SHIFT_REGISTER] = sr

    ow.zones.registry.register_zone_type(
        ZONE_TYPE_SHIFT_REGISTER, ShiftRegisterZone, create_zone
    )


def create_zone(ow: "OpenWater", zone_data: dict) -> "ShiftRegisterZone":
    attr_schema = {"sr_idx": {"type": "integer", "required": True}}
    v: Validator = Validator(attr_schema)
    v.allow_unknown = True
    if not v.validate(zone_data["attrs"]):
        raise ZoneValidationException("ShiftRegisterZone validation failed", v.errors)
    return ShiftRegisterZone.of(ow, zone_data)


class ShiftRegisterZone(BaseZone):
    ATTR_SCHEMA = {"sr_idx": {"type": "integer", "required": True}}

    def __init__(
        self,
        ow: "OpenWater",
        id_: int,
        name: str,
        zone_type: str,
        is_master: bool,
        attrs: dict,
    ):
        super().__init__(ow, id_, name, zone_type, is_master, attrs)
        self._sr: "ShiftRegister" = ow.data[DATA_SHIFT_REGISTER]
        self._sr_idx = attrs.get("sr_idx")

    @property
    def extra_attrs(self):
        return {"sr_idx": self._sr_idx}

    def is_open(self) -> bool:
        return bool(self._sr.get_reg_status(self._sr_idx))

    async def open(self) -> None:
        await self._sr.async_turn_on(self._sr_idx)

    async def close(self) -> None:
        await self._sr.async_turn_off(self._sr_idx)

    def get_zone_type(self) -> str:
        return "SHIFT_REGISTER"

    @staticmethod
    def get_additional_config(ow: "OpenWater"):
        sr = ow.data[DATA_SHIFT_REGISTER]
        num_reg = sr.num_regs
        return {
            "sr_idx": {
                "type": "select",
                "label": "Physical Shift Register Index",
                "options": list(range(num_reg)),
            }
        }


class ShiftRegister:
    def __init__(
        self,
        ow: "OpenWater",
        gpio: "OWGpio",
        data_pin: int,
        clock_pin: int,
        oe_pin: int,
        latch_pin: int,
        num_regs: int,
        active_high: bool = True,
    ):
        self.ow = ow
        self.g = gpio
        self.data_pin = data_pin
        self.clock_pin = clock_pin
        self.oe_pin = oe_pin
        self.latch_pin = latch_pin
        self.num_regs = num_regs
        self.active_high = active_high
        self._reg_mask = 0

    def write_registers(self) -> None:
        self.g.low([self.clock_pin, self.latch_pin])
        for reg in range(self.num_regs):
            self.g.low(self.clock_pin)
            if 1 & (self._reg_mask >> reg):
                self.g.high(self.data_pin)
            else:
                self.g.low(self.data_pin)
            self.g.high(self.clock_pin)
        self.g.high(self.latch_pin)

    async def async_write_registers(self) -> None:
        await self.g.async_low([self.clock_pin, self.latch_pin])
        for reg in range(self.num_regs):
            await self.g.async_low(self.clock_pin)
            if 1 & (self._reg_mask >> reg):
                await self.g.async_high(self.data_pin)
            else:
                await self.g.async_low(self.data_pin)
            await self.g.async_high(self.clock_pin)
        await self.g.async_high(self.latch_pin)

    def turn_on(self, reg: int) -> None:
        if reg > self.num_regs - 1:
            raise ZoneException(
                "Attempted to turn on register {}, but SR only has {} registers",
                reg,
                self.num_regs,
            )

        if self.active_high:
            self._reg_mask |= 1 << reg
        else:
            self._reg_mask ^= 1 << reg

        self.write_registers()

    async def async_turn_on(self, reg: int) -> None:
        if reg > self.num_regs - 1:
            raise ZoneException(
                "Attempted to turn on register {}, but SR only has {} registers",
                reg,
                self.num_regs,
            )

        if self.active_high:
            self._reg_mask |= 1 << reg
        else:
            self._reg_mask ^= 1 << reg

        await self.async_write_registers()

    def turn_off(self, reg: int) -> None:
        if reg > self.num_regs - 1:
            raise ZoneException(
                "Attempted to turn off register {}, but SR only has {} registers",
                reg,
                self.num_regs,
            )

        if self.active_high:
            self._reg_mask ^= 1 << reg
        else:
            self._reg_mask |= 1 << reg

        self.write_registers()

    async def async_turn_off(self, reg: int) -> None:
        if reg > self.num_regs - 1:
            raise ZoneException(
                "Attempted to turn off register {}, but SR only has {} registers",
                reg,
                self.num_regs,
            )

        if self.active_high:
            self._reg_mask ^= 1 << reg
        else:
            self._reg_mask |= 1 << reg

        await self.async_write_registers()

    def disable_output(self) -> None:
        self.g.high(self.oe_pin)

    async def async_disable_outputs(self):
        await self.g.async_high(self.oe_pin)

    def get_reg_status(self, reg: int):
        return 1 & (self._reg_mask >> reg)
