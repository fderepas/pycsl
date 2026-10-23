"""v53 DISAGREE — ROUTE #89. A CONDITIONAL store to a LIST field: route #83's `(any int)`
override is gated on `field_types not in _NONSCALAR`, so it fenced SCALARS ONLY, and routes
#85/#87 re-armed the gap by making a field literal's contents faithful. The model took the
nested store's literal UNCONDITIONALLY. Constructed with `C(0)`, so CPython returns 1."""
from typing import List


class C:
    xs: List[int]

    #@ assigns self.xs
    def __init__(self, k: int) -> None:
        self.xs = [1, 2]
        if k > 0:
            self.xs = [7, 8]


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    c = C(0)
    return c.xs[0]


if __name__ == "__main__":
    print(f())
