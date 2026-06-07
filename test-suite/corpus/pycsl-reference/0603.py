"""Test 0603 — isinstance on a class-typed value: no type/constant name collision (07-0647-spec S1.2/R9).

`isinstance(x, Box)` used the class name `Box` both as a record TYPE (`type box`) and as an
opaque VALUE constant (`val constant box`) — a name collision and a type error (the record-typed
`x` passed to an `int`-typed check). The class-as-value now gets a distinct name and the check is
polymorphic in its receiver. RED on the prior commit.
"""
# pycsl-flags: --memory-model hoare
#@ class invariant self.v >= 0
class Box:
    def __init__(self) -> None:
        self.v: int = 0


#@ ensures \result == 1 or \result == 0
#@ assigns \nothing
def check(x: Box) -> int:
    if isinstance(x, Box):
        return 1
    return 0
