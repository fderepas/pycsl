"""v54 DISAGREE — ROUTE #89's DICT arm. Kept separate from v53 because #85 and #87 are two
different captures reached through two different arms of `_field_default`, and a repair that
fixed only one would satisfy the other's driver by accident. CPython returns 5."""
from typing import Dict


class C:
    d: Dict[int, int]

    #@ assigns self.d
    def __init__(self, k: int) -> None:
        self.d = {1: 5}
        if k > 0:
            self.d = {1: 9}


#@ ensures \result == 9
#@ assigns \nothing
def f() -> int:
    c = C(0)
    return c.d[1]


if __name__ == "__main__":
    print(f())
