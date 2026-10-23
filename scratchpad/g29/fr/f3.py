r"""G29 FR3 — a list param passed to a builtin that mutates it in place: `heapq.heapify`."""
import heapq
from typing import List
_ = 0  # anchor


#@ requires len(xs) == 2
#@ assigns \nothing
def f(xs: List[int]) -> None:
    heapq.heapify(xs)


#@ requires len(xs) == 2 and xs[0] == 5 and xs[1] == 1
#@ ensures \result == 5
def probe(xs: List[int]) -> int:
    f(xs)
    return xs[0]


if __name__ == "__main__":
    print("CPython:", probe([5, 1]))
