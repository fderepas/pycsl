r"""Test 3097 — route #280 CONTROLS (expected PASS): a method that writes nothing (`assigns \nothing`)
called on a tuple element, and a READ of a dict value (`len(d[0])`), are untouched by the
computed-receiver mutator refusal and keep proving.
"""
# pycsl-expected: PASS
from typing import Dict, List, Tuple


class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ assigns \nothing
    def get(self) -> int:
        return 3


#@ ensures \result == 0
#@ assigns \nothing
def pure_method() -> int:
    c = C()
    t: Tuple[C, int] = (c, 1)
    t[0].get()
    return c.v


#@ requires 0 in d
#@ ensures \result == len(d[0])
#@ assigns \nothing
def read_value(d: Dict[int, List[int]]) -> int:
    return len(d[0])


if __name__ == "__main__":
    assert pure_method() == 0
    assert read_value({0: [1, 2]}) == 2
