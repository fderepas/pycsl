r"""staticmethod decorator on module function"""
from typing import Callable, List
_ = 0  # anchor


@staticmethod
def g() -> int:
    return 3


#@ ensures \result == 0
def probe() -> int:
    return g()


if __name__ == "__main__":
    print("CPython:", probe())
