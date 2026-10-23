r"""mutable_state class method mutating param list with assigns nothing"""
from typing import List, Dict
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.k = 0

    #@ assigns \nothing
    def m(self, xs: List[int]) -> None:
        xs[0] = 9


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [0]
    c = C()
    c.m(xs)
    return xs[0]


if __name__ == "__main__":
    print("CPython:", probe())
