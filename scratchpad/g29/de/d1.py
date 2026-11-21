r"""custom decorator changing result"""
from typing import Callable, List
_ = 0  # anchor


def double(f: Callable[[], int]) -> Callable[[], int]:
    def inner() -> int:
        return f() * 2
    return inner


@double
def g() -> int:
    return 3


#@ ensures \result == 3
def probe() -> int:
    return g()


if __name__ == "__main__":
    print("CPython:", probe())
