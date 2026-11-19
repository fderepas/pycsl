# pycsl-flags: --memory-model hoare
"""d45 RETURNS — the AGREE twin of d44 and route #89's over-breadth bound on the EXCEPTION
surface. With NO conditional store the field keeps route #87's faithful literal, so the length
is known, index 1 is in range, and this must still PROVE. Without it, d44 would be satisfied
by an emitter that simply refused every list-field subscript."""
from typing import List


class C:
    xs: List[int]

    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs = [1, 2]


#@ requires True
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.xs[1]


if __name__ == "__main__":
    f()
