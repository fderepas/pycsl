r"""Test 1995 — gen #36 (expected FAIL, refused): ROUTE #233 — `except E as e` read as an opaque constant

The handler is modelled without its exception object, so both reads of `e` were ONE opaque
`val constant e`, and `a == b` PROVED at 87ff222f. CPython: two distinct ValueError objects
compare unequal, `\result == 0`.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 1
#@ assigns \nothing
def f(x: int) -> int:
    r = 0
    try:
        raise ValueError(x)
    except ValueError as e:
        a = e
    try:
        raise ValueError(x + 1)
    except ValueError as e:
        b = e
    if a == b:
        r = 1
    return r
