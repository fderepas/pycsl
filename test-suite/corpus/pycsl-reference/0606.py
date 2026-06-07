"""Test 0606 — method receiver present + class-returning function typed faithfully (07-0647-spec S3.1/S4/R11/R13).

A method body referencing `self.<field>` MUST have `self` in scope (R11); a function returning a
class instance MUST be typed as that record end-to-end, not `int` (R13). Both hold here:
`C.get` reads `self.v`, and `make` returns a `Box` typed as the record.
"""
# pycsl-flags: --memory-model hoare
#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ ensures \result == self.v
    #@ assigns \nothing
    def get(self) -> int:
        return self.v


#@ ensures True
#@ assigns \nothing
def make() -> C:
    return C()
