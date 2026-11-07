r"""mutable_state set param mutated, contract reads it"""
from typing import List, Set, Dict
_ = 0  # anchor


#@ mutable_state
class C:
    def __init__(self) -> None:
        self.k = 0

    #@ requires 1 not in s
    #@ ensures 1 not in s
    #@ assigns \nothing
    def m(self, s: Set[int]) -> None:
        s.add(1)


#@ ensures \result == 0
def probe() -> int:
    c = C()
    s: Set[int] = set()
    c.m(s)
    return len(s)


if __name__ == "__main__":
    print("CPython:", probe())
