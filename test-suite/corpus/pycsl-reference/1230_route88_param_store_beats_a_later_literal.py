"""Test 1230 — ROUTE #88 RUNNING IN THE OTHER DIRECTION, which is what shows the model had no
notion of store ORDER at all rather than a preference for literals.

`construction_synth._collect_init_construction` **APPENDED** to `init_body` for every top-level
param-dependent store, so an EARLIER param store survived a LATER one that superseded it. Here
the model takes `self.n = k` and the real program takes `self.n = 3`. Measured before the
repair: this claim PROVED for `C(7)`, CPython returns 3, and the TRUE twin (1231) was REFUSED.

Keep this file paired with 1228: between them they say the defect is not "the emitter prefers
literals" and not "the emitter prefers parameters" — it is that BOTH value-supplying paths were
keyed on a store rather than on the LAST store.

This file is `pycsl-expected: FAIL`.
"""
# pycsl-expected: FAIL


class C:
    n: int

    #@ assigns self.n
    def __init__(self, k: int) -> None:
        self.n = k
        self.n = 3


#@ requires True
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    c = C(7)
    return c.n
