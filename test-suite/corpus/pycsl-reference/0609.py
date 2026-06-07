"""Test 0609 — `\result.<field>` constrains a record-returning function (07-0903 W2).

A function returning a class instance can now be SPECIFIED: `#@ ensures \result.v == 0`
references the field of the returned record (lowered to `result.v`). Previously `\result.field`
did not parse, so such a factory could only carry a vacuous `ensures True`. Pairs with the
already-supported tuple form `\result[k]` (0587).
"""
# pycsl-flags: --memory-model hoare
#@ class invariant self.v >= 0
class Box:
    def __init__(self) -> None:
        self.v: int = 0


#@ ensures \result.v == 0
#@ assigns \nothing
def make() -> Box:
    return Box()
