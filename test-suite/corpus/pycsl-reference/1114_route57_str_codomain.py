"""Test 1114 — ROUTE #57 negative witness (c): the `str` CODOMAIN, which is what makes
this route strictly broader than route #56.

FALSE OF THE PROGRAM: `{1: "a"}.get(5)` is `None` and `None == ""` is False, so `f`
returns 0.

ROUTE #56 WAS CONFINED TO THE `int` CARRIER BY A TYPE ACCIDENT: its `""` sentinel was
ill-typed against the comparand and the emission died on a Why3 type error, which is
why routes #50 and #51 probed that class at `str` and found nothing. **There is no
such accident here.** The `.get` lowering picks its sentinel FROM THE CODOMAIN TYPE,
so it is type-correct by construction at every codomain — and every codomain decides.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Dict


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d: Dict[int, str] = {1: "a"}
    if d.get(5) == "":
        return 1
    return 0
