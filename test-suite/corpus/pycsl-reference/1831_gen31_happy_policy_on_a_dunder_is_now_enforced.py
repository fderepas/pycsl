r"""Test 1831 — gen #31 (expected FAIL): a `#@ happy ... postcond` policy TARGETING A DUNDER
is now enforced.

ROUTE #219's third and sharpest carrier. `#@ happy` is the trust-boundary surface: a NAMED
property attached to a target method and discharged as an ordinary contract. Module 3
attaches it by walking the AST, WHERE DUNDERS ARE PRESENT, so its "a missing target is a
hard error" refusal never fired — and Module 5 then dropped the method, so nothing was ever
checked. `self.v = 0` from 5 plainly violates `self.v >= \old(self.v)` and the file reported

    [+] Verification SUCCESS! All contracts formally proven.

Renaming `__enter__` to `bump` made the identical file FAIL (corpus 1832). It matters more
than #219's other two carriers because `happy` is the surface a reader points at to say
"this property holds across this module", and the enforcement was decided by the target's
NAME.
"""
# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL
#@ happy no_decrease:
#@     targets __enter__
#@     postcond self.v >= \old(self.v)
class C:
    def __init__(self) -> None:
        self.v: int = 5

    #@ assigns self.v
    def __enter__(self) -> int:
        self.v = 0
        return 0
