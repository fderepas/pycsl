r"""class constant int read via instance after class rebind in a method"""
from typing import List, Dict, Optional
_ = 0  # anchor


class C:
    N = 3

    def __init__(self) -> None:
        self.k = 0

    def bump(self) -> None:
        C.N = 5


#@ ensures \result == 3
def probe() -> int:
    c = C()
    c.bump()
    return C.N


if __name__ == "__main__":
    print("CPython:", probe())
