"""Test 1272 — route #96 CONTROL: the FIELD arm of the 2x2 was ALREADY framed, and still is.

The 2026-08-26 `trusted-frame-oracle` fix gave a bodyless `val` its `writes` for a
`self.<field>` assigns; route #96 is the ARRAY-REGION cell of the same 2x2, which that fix left
untouched. This file pins the field cell so the region repair cannot regress it: a `\trusted`
method declaring `#@ assigns self.f` must still deny its caller the stale field value.

Together with 1267 (region, now refused) this witnesses that BOTH cells of the bodyless-val row
declare their frame, and that they got there by two independent repairs.
"""
# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL


class Box:
    def __init__(self):
        self.f: int = 7

    #@ assigns self.f
    #@ \trusted reviewer: route96
    def clobber(self) -> int:
        self.f = 0
        return 0


#@ ensures \result == 7
def driver() -> int:
    b = Box()
    b.clobber()
    return b.f
