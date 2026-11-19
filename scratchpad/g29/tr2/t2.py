r"""trusted method mutating despite assigns nothing"""
from typing import List, Dict
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ \trusted
    #@ assigns \nothing
    def m(self) -> None:
        self.v = 5


#@ ensures \result == 0
def probe() -> int:
    c = C()
    c.m()
    return c.v


if __name__ == "__main__":
    print("CPython:", probe())
