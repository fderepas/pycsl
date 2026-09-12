# pycsl-flags: --memory-model hoare
"""d42 RAISES — a missing-key subscript of a DICT FIELD whose literal is now modelled
faithfully (route #85). The field is `{1: 5}`, so `c.d[9]` is a KeyError, which `\all`
claims, so PyCSL must REFUSE.

Before route #85 the field was the EMPTY map, which made the missing-key answer DECIDABLE in
the wrong direction — that is exactly what route #48's closing note says an empty collection
does. So this driver is only meaningful now that the contents are real."""
from typing import Dict


class C:
    d: Dict[int, int]

    #@ assigns self.d
    def __init__(self) -> None:
        self.d = {1: 5}


#@ requires True
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.d[9]


if __name__ == "__main__":
    f()
