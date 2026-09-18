r"""method mutating param dict"""
from typing import List, Dict
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.k = 0

    #@ assigns \nothing
    def m(self, d: Dict[str, int]) -> None:
        d["a"] = 9


#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 0}
    c = C()
    c.m(d)
    return d["a"]


if __name__ == "__main__":
    print("CPython:", probe())
