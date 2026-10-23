# pycsl-flags: --memory-model hoare
"""d44 RAISES — ROUTE #89. The CONDITIONAL store in `__init__` makes the list field's contents
UNKNOWN, so its LENGTH is unknown too and an index of 5 cannot be shown safe. CPython with
`C(0)` builds `[1, 2]` and raises IndexError. PyCSL must REFUSE.

THIS PAIR IS THE EXCEPTION SIDE OF ROUTE #89 AND IT IS NOT IMPLIED BY THE VALUE SIDE. Route
#89's repair replaces a decidable wrong array with an unconstrained one; whether the
IndexError obligation is still generated over an `any_array` — rather than quietly discharged
or quietly erased — is a separate measurement, and d45 is the twin that keeps this from being
satisfiable by refusing everything."""
from typing import List


class C:
    xs: List[int]

    #@ assigns self.xs
    def __init__(self, k: int) -> None:
        self.xs = [1, 2]
        if k > 0:
            self.xs = [7, 8]


#@ requires True
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    c = C(0)
    return c.xs[5]


if __name__ == "__main__":
    f()
