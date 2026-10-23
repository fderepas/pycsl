r"""functools decorator import"""
from typing import Callable, List
_ = 0  # anchor


import functools


@functools.lru_cache()
def g(x: int) -> int:
    return x + 1


#@ ensures \result == 0
def probe() -> int:
    return g(1)


if __name__ == "__main__":
    print("CPython:", probe())
