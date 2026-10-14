r"""Test 1996 — gen #36 (expected FAIL, refused): ROUTE #234 — a guarded constructor arm skipped the next arm

In the native Why3 `match`, a failed guard fell through to the wildcard body (or `()`), so
the `case MSome(n):` arm was skipped and `\result == 7` PROVED at 87ff222f. CPython: the guard
fails on -5, the second arm sets r = 2.
"""
#@ datatype Maybe = MNone | MSome(int)
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    r = 7
    o = MSome(-5)
    match o:
        case MSome(n) if n > 0:
            r = 1
        case MSome(n):
            r = 2
        case MNone():
            r = 3
    return r
