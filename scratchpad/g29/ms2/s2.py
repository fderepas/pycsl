r"""mutable_state list param mutated not in contract"""
from typing import List, Set, Dict
_ = 0  # anchor


#@ mutable_state
class C:
    def __init__(self) -> None:
        self.k = 0

    #@ assigns \nothing
    def m(self, xs: List[int]) -> None:
        xs.append(1)


#@ ensures \result == 0
def probe() -> int:
    c = C()
    xs: List[int] = []
    c.m(xs)
    return len(xs)


if __name__ == "__main__":
    print("CPython:", probe())
