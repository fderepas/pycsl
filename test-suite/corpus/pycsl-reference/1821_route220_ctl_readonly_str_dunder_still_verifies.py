r"""Test 1821 — ROUTE #220 CONTROL (expected PASS): a READ-ONLY `__str__` is untouched.

Route #220's repair frames the `val` minted for an explicitly-called `__str__` with the
self-fields its dropped body writes. A `__str__` whose body writes NOTHING must still be
modelled pure, so this file must still verify — otherwise the repair would be a blanket
"a `__str__()` call clobbers the receiver", which is exactly the over-broad shape route
#13's census refused once already.
"""
# pycsl-expected: PASS


#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v: int = 0

    def __str__(self) -> str:
        return "x"


#@ ensures \result == 0
def use() -> int:
    c = C()
    before: int = c.v
    _s: str = c.__str__()
    after: int = c.v
    return before - after
