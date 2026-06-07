"""Test 0610 — negative: a false `\result.<field>` claim is unprovable (07-0903 W2).

Same record-returning `make` as 0609, but `#@ ensures \result.v == 1` over-claims while the
constructed `Box` has `v == 0`. The VC refutes it — confirming `\result.v` reads the real field,
not an opaque value.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
#@ class invariant self.v >= 0
class Box:
    def __init__(self) -> None:
        self.v: int = 0


#@ ensures \result.v == 1
#@ assigns \nothing
def make() -> Box:
    return Box()
