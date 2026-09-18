r"""module constant rebound via global in a function called at module scope"""
from typing import List, Dict
_ = 0  # anchor


N = 3


def bump() -> None:
    global N
    N = 5


bump()


#@ ensures \result == 3
def probe() -> int:
    return N


if __name__ == "__main__":
    print("CPython:", probe())
