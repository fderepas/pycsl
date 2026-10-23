"""Test 1084 — ROUTE #49 control: `a += 1` on an INT parameter is FAITHFUL and must keep
proving.

TRUE OF THE PROGRAM: Python returns 2.

The half of route #49's second shape that must NOT be refused, and the reason its guard is
keyed on the target being a COLLECTION rather than on it being a parameter. Python integers
are IMMUTABLE, so `a += 1` inside a callee rebinds the local name and the caller genuinely
does not see it — the local-update model is exactly right. A refusal written against
"augmented assignment to a parameter" would make this file fail, and this is the far more
common shape.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires a == 1
#@ ensures \result == 2
#@ assigns \nothing
def f(a: int) -> int:
    a += 1
    return a
