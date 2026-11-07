"""Test 1088 — ROUTE #50 control: the defect is `@mutable_state`-GATED.

FALSE OF THE PROGRAM: Python returns 0, exactly as in 1085.

The same file as 1085 WITHOUT the decorator. It fails closed at the parent commit too, and
that is the point: it localises the route to the `@mutable_state` string-local
classification rather than to `is None` in general. Kept because a future widening of that
classification would silently widen the route, and this file is what would notice.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@dataclass
class C:
    tag: int = 0

    #@ requires c < 0
    #@ requires t == "x"
    #@ ensures \result == 7
    def m(self, c: int, t: str) -> int:
        s = t
        s = None
        if c > 0:
            s = t
        if s is None:
            return 0
        return 7


if __name__ == "__main__":
    o = C()
    assert o.m(-1, "x") == 0
