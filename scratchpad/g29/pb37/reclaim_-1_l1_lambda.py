from typing import Callable
_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    f: Callable[[int], int] = lambda x: x + 1
    return f(1)
