"""Test 1243 — ROUTE #90: the annotation arm fired on a LOCAL too, not only a param.

NOT TRUE OF THE PROGRAM. `y: bool = 1` binds the int 1; `1 is True` is False, so CPython
returns 0. MEASURED: f() = 0. This witness matters because a repair scoped to PARAMETERS
would leave the local arm proving — the symbol table carries annotated locals as well.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    y: bool = 1
    if y is True:
        return 1
    return 0
