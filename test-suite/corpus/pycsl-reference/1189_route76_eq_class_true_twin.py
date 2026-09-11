"""1189 — ROUTE #76 ANTI-VACUITY: the TRUE twin of 1188 does not prove.

CPython answers `dup(a) != a` -> True, so `\\result != x` is TRUE OF THE PROGRAM. The model
cannot discharge it, because it decides the comparison STRUCTURALLY and the two records
have equal fields. Both directions measured is what makes #76 a ROUTE and not a gap: the
false claim proved and the true claim did not.

Kept as `FAIL` so that a future model which genuinely tracks object identity — the stated
reopening capability for #76's residue — announces itself HERE by starting to pass.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare


class C:
    v: int

    def __init__(self, v: int) -> None:
        self.v = v


#@ ensures \result != x
#@ assigns \nothing
def dup(x: C) -> C:
    return C(x.v)
