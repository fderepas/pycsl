r"""Test 1801 — WITNESS: a `#@ happy ... protects` policy refuses a non-exempt TRUSTED
function whose DECLARED `assigns` writes a protected path without `#@ \preserves`.

This is route #209's boundary, and it had no witness of any kind. It LOOKED covered:
`bin/check-happy-trust-boundaries.py` holds a route-#209 case and has been green every
run. Measured, that case's carrier (`#@ \trusted` + `#@ assigns g.v` over a body
`g.v = n`) was being refused by ROUTE #210's check — "its BODY writes the protected path" —
so the `\preserves` refusal was never exercised there either. Two instruments disagreed
(`check-refusal-witness-coverage` listed the site as undemonstrated all along) and neither
had been read against the other.

THE ISOLATING SHAPE, and it is the point of this file: the function DECLARES the protected
path in `#@ assigns` and does NOT write it in its body. Route #210's body check cannot
fire; only the declared-frame check can. `#@ \trusted` means the body is never lowered, so
the declared frame is all the model has — a false one is a hole, which is why the policy
demands `#@ \preserves` or an `except` entry.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor

#@ happy own:
#@     protects g.v
#@     except setter

#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v: int = 0


g = C()


#@ requires n >= 0
#@ assigns g.v
def setter(n: int) -> None:
    g.v = n


#@ requires n >= 0
#@ assigns g.v
#@ \trusted
def declares_but_does_not_write(n: int) -> None:
    return
