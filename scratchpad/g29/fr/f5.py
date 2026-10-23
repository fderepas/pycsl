r"""G29 FR5 — `d.update(...)` on a dict PARAMETER under `assigns \nothing`."""
from typing import Dict
_ = 0  # anchor


#@ assigns \nothing
def f(d: Dict[int, int]) -> None:
    d.update({1: 9})


#@ requires 1 in d and d[1] == 5
#@ ensures \result == 5
def probe(d: Dict[int, int]) -> int:
    f(d)
    return d[1]


if __name__ == "__main__":
    print("CPython:", probe({1: 5}))
