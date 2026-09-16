r"""G29 FR7 — a list parameter's slice assigned under `assigns \nothing`."""
from typing import List
_ = 0  # anchor


#@ requires len(xs) == 2
#@ assigns \nothing
def f(xs: List[int]) -> None:
    xs[0:2] = [9, 9]


#@ requires len(xs) == 2 and xs[0] == 5
#@ ensures \result == 5
def probe(xs: List[int]) -> int:
    f(xs)
    return xs[0]


if __name__ == "__main__":
    print("CPython:", probe([5, 1]))
