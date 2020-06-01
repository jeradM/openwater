from typing import Callable


def blocking(func: Callable):
    setattr(func, "_ow_blocking", True)
    return func


def is_blocking(func: Callable):
    return getattr(func, "_ow_blocking", False) is True


def nonblocking(func: Callable) -> Callable:
    setattr(func, "_ow_nonblocking", True)
    return func


def is_nonblocking(func: Callable) -> bool:
    return getattr(func, "_ow_nonblocking", False) is True
