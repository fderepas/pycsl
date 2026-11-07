"""Test 1019 — ROUTE #34: an ALIAS then an APPEND, which defeats the one
invalidation that did exist.

FALSE OF THE PROGRAM: `b.append(7)` grows the list `a` also refers to, so
`len(a)` is 1 and Python returns 7. Proved `\result == 0` at c4233fed.

`_current_append_targets` tracks the name the append is written on — `b` — so the
size fold for `a` stayed at the empty literal's 0 and the guard `len(a) > 0`
lowered to `0 > 0`. An invalidation keyed on the SYNTAX of the mutation misses
every alias of the object.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a = []
    b = a
    b.append(7)
    return a[0] if len(a) > 0 else 0
