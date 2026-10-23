"""Test 1101 — ROUTE #51 shape (b): a `str`-declared dataclass FIELD tested `is None`.

FALSE OF THE PROGRAM: Python takes the `is None` branch and `o.probe()` returns 0 after a
caller has stored `None` in the field.

The second way to reach route #50's always-present answer with no binding in the function.
A `dataclass` field annotation is not enforced by Python either, and the field's value
comes from OUTSIDE the method, so nothing in the body could establish its non-None-ness.
At the parent commit `27cf17b1` `\result == 7` PROVED.

Fixed with 1100 by the same one-line rule — ALWAYS-PRESENT IS A CLAIM ABOUT A BINDING, so
it may only be made about a name this function BINDS. `self.name` is not such a name.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    name: str = ""

    #@ requires True
    #@ ensures \result == 7
    #@ assigns \nothing
    def probe(self) -> int:
        if self.name is None:
            return 0
        return 7


if __name__ == "__main__":
    o = C()
    o.name = None
    assert o.probe() == 0
