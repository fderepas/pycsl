r"""class constant rebound via setattr at module scope"""
from typing import List, Dict
_ = 0  # anchor


class C:
    N = 3

    def __init__(self) -> None:
        self.k = 0


setattr(C, "N", 5)


#@ ensures \result == 3
def probe() -> int:
    return C.N


if __name__ == "__main__":
    print("CPython:", probe())
