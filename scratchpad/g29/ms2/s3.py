r"""mutable_state dict param mutated"""
from typing import List, Set, Dict
_ = 0  # anchor


#@ mutable_state
class C:
    def __init__(self) -> None:
        self.k = 0

    #@ assigns \nothing
    def m(self, d: Dict[int, int]) -> None:
        d[1] = 1


#@ ensures \result == 0
def probe() -> int:
    c = C()
    d: Dict[int, int] = {}
    c.m(d)
    return len(d)


if __name__ == "__main__":
    print("CPython:", probe())
