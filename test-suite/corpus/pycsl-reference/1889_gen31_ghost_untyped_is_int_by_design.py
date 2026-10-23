r"""Test 1889 — gen #31 CONTROL for 1886 (expected PASS): an UNTYPED ghost is still `int`.

The (u4) counter-program for the ghost-keyword refusal: the strongest program the rule
could forbid is the one annotations.md §11 explicitly blesses — "untyped ghost declarations
(`#@ ghost <name> = <expr>`) default to `int`". That is the documented case, it must keep
working, and the refusal is written to skip a `None` declared type so that it does.

Without this file the rule would be one `if` away from forbidding the form its own
documentation recommends.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ requires x > 0
#@ ensures \result == x
#@ assigns \nothing
def f(x: int) -> int:
    #@ ghost g = 0
    return x
