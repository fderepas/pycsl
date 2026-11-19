from typing import Callable
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    n: int = 5

    def inner() -> int:
        return n

    n = 7
    return inner()
