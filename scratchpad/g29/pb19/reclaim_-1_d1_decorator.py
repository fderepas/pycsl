from typing import Callable
_ = 0  # anchor


def double(fn: Callable[[], int]) -> Callable[[], int]:
    def w() -> int:
        return fn() * 2
    return w


@double
def f() -> int:
    return 3


#@ ensures \result == -1
def probe() -> int:
    return f()
