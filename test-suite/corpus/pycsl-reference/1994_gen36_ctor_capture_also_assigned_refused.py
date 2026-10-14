r"""Test 1994 — gen #36 (expected FAIL, refused): ROUTE #233 — a constructor-pattern capture that is also a local

`a` is both an assigned local and a `Some(a)` capture; the native arm's pattern variable and
the local are different Why3 variables, so the shape is refused fail-closed. CPython returns 7.
"""
#@ datatype Box = Some(int) | Empty
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    a = 0
    o = Some(7)
    match o:
        case Some(a):
            return a
        case Empty():
            return a
