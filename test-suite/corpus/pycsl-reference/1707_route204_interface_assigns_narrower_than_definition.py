r"""Test 1707 — ROUTE #204: `#@ interface assigns \nothing` over a definition that really
writes `a[0]`. `_emit_narrowing_vc` proves the interface weakens the definition for
`ensures` and `requires` and emits NOTHING for `assigns`, while Module 5 carries
`interface.assigns` into the IR and IMPORTERS frame the call with it. MEASURED: an
importer of this module proved `\result == 0` for `x = a[0]; bump(a); return x - a[0]`
while CPython answers -4 for `a = [1]`, an argument the precondition admits. The context
was NOT inconsistent — the absurd twin `\result == 999` was refused and the non-vacuity
gate stayed silent — because the narrow frame plus the inherited `ensures a[0] == 5`
merely force the caller into "the element was already 5", which is satisfiable and false
of the call. An interface frame may claim MORE writes than the definition, never FEWER.
"""
# pycsl-expected: FAIL
from typing import List

_ = 0  # anchor


#@ requires \length(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == 5
#@ interface assigns \nothing
#@ interface requires \length(a) >= 1
def bump(a: List[int]) -> None:
    a[0] = 5
