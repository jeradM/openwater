import asyncio

try:
    import RPi.GPIO as GPIO
except Exception:
    print("Failed to import GPIO module. You probably need superuser privileges (sudo)")

from fake_rpi.RPi import GPIO as gpio
from typing import TYPE_CHECKING, Optional, Union, Collection

if TYPE_CHECKING:
    from openwater.core import OpenWater

DATA_GPIO = "GPIO"


def setup_plugin(ow: "OpenWater", config: dict = {}):
    ow.async_add_task(gpio.setmode, gpio.BCM)
    ow.data[DATA_GPIO] = OWGpio(ow)


class OWGpio:
    def __init__(self, ow: "OpenWater"):
        self.ow = ow
        self.LOW = gpio.LOW
        self.HIGH = gpio.HIGH
        self.IN = gpio.IN
        self.OUT = gpio.OUT

    def set_output(self, pin: Union[Collection[int], int]) -> None:
        gpio.setup(pin, self.OUT)

    def async_set_output(self, pin: Union[Collection[int], int]) -> None:
        self.ow.run_in_executor(gpio.setup, pin, self.OUT)

    def set_input(self, pin: Union[Collection[int], int]) -> None:
        gpio.setup(pin, self.IN)

    def async_set_input(self, pin: Union[Collection[int], int]) -> None:
        self.ow.run_in_executor(gpio.setup, pin, self.IN)

    def output(self, pin: Union[Collection[int], int], state: int) -> None:
        gpio.output(pin, state)

    def async_output(self, pin: Union[Collection[int], int], state: int) -> None:
        self.ow.run_in_executor(gpio.output, pin, state)

    def low(self, pin: Union[Collection[int], int]) -> None:
        self.output(pin, self.LOW)

    def async_low(self, pin: Union[Collection[int], int]) -> None:
        self.async_output(pin, self.LOW)

    def high(self, pin: Union[Collection[int], int]) -> None:
        self.output(pin, self.HIGH)

    def async_high(self, pin: Union[Collection[int], int]) -> None:
        self.async_output(pin, self.HIGH)

    def input(self, pin: int, state: int) -> int:
        return gpio.input(pin, state)

    def async_input(self, pin: int) -> asyncio.Future:
        return self.ow.create_future(gpio.input, pin)
