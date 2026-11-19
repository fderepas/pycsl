# pycsl-flags: --memory-model hoare
"""d40 RAISES — an out-of-range subscript of a LIST FIELD whose literal is now modelled
faithfully (route #87). The field is `[1, 2, 3]`, so index 5 is an IndexError. The contract
claims `\all`, which includes IndexError, so PyCSL must REFUSE.

This pair exists because route #87 made a list field's CONTENTS decidable for the first time.
A repair that supplies real contents also supplies a real LENGTH to reason about, and the
exception side of that is not implied by the value side — it has to be measured too."""
from typing import List


class C:
    xs: List[int]

    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs = [1, 2, 3]


#@ requires True
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.xs[5]


if __name__ == "__main__":
    f()
