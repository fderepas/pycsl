"""Test 1070 — ROUTE #47 negative witness (a): a `getattr` DEFAULT was the integer 0.

FALSE OF THE PROGRAM: `{} == 0` is False in Python, so `f()` returns 0.

`_lower_getattr`'s absent path coerced a NON-scalar default to the literal `0`, with the
comment "the dict/list content is then unmodeled (fails-safe)". It is not fails-safe: an
UNMODELLED value is undecidable and the integer `0` is DECIDABLE, so the guard was decided
against a value Python never produces. At the parent commit d7ce974c `\\result == 7` PROVED.

FOUND BY `bin/check-singleton-constant-lowering.py`, the twenty-fifth plane, within minutes
of that plane being written — which is the argument for writing the plane. Route #22
(witness 0991) had closed the DECLARED case and deliberately left ABSENCE alone: correct
about WHICH value is returned, silent about how that value is MODELLED.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    #@ requires True
    #@ ensures True
    def __init__(self) -> None:
        self.x = 1


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    c = C()
    d = getattr(c, "missing", {})
    if d == 0:
        return 7
    return 0
