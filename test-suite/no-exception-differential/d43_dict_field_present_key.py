# pycsl-flags: --memory-model hoare
"""d43 RETURNS — the present-key twin of d42. `c.d[1]` is 5 and nothing raises."""
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
    return c.d[1]


if __name__ == "__main__":
    f()
