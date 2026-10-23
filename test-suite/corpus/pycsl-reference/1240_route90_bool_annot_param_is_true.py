"""Test 1240 — ROUTE #90: `is True` on a `bool`-ANNOTATED PARAM must NOT prove.

NOT TRUE OF THE PROGRAM. `requires x == 1` is satisfied by the int `1` (Python: `1 ==
True` is True), and `1 is True` is **False**, so CPython returns 0. MEASURED: f(1) = 0.

Before route #90 this PROVED `\result == 1`: the whitelist admitted the operand because
the symbol table said `bool`, and the symbol table is built from the ANNOTATION. The
emission was literally `if (x = 1)` under `requires { (x = 1) }` — a trivially true guard.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires x == 1
#@ ensures \result == 1
#@ assigns \nothing
def f(x: bool) -> int:
    if x is True:
        return 1
    return 0
