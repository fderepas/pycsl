r"""Test 1993 — gen #36 (expected FAIL, refused): ROUTE #233 — a constructor-pattern capture read after its `match`

`case Some(v):` binds `v` inside the native Why3 arm only; the reads of `v` AFTER each `match`
were one opaque constant, so `r - v == 0` PROVED at 87ff222f. CPython returns 7 - 8 = -1.
"""
#@ datatype Box = Some(int) | Empty
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    o = Some(7)
    match o:
        case Some(v):
            pass
        case Empty():
            pass
    r = v
    o2 = Some(8)
    match o2:
        case Some(v):
            pass
        case Empty():
            pass
    return r - v
