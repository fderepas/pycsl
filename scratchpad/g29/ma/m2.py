r"""G29 MA2 — a module function mutates a list PARAMETER through a local alias, declaring `assigns \nothing`."""
from typing import List
_ = 0  # anchor


#@ requires len(ys) >= 1
#@ assigns \nothing
def m(ys: List[int]) -> None:
    zs = ys
    zs[0] = 9


#@ requires len(ys) >= 1
#@ ensures \result == ys[0]
def probe(ys: List[int]) -> int:
    before = ys[0]
    m(ys)
    return before


if __name__ == "__main__":
    ys = [1, 2]
    print("CPython:", probe(ys), ys[0])
