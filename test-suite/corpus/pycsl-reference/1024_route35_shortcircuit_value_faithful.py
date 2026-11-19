"""Test 1024 — ROUTE #35 POSITIVE witness: `and`/`or` return the selected operand.

`0 or 5` is 5 and `3 and 7` is 7 in Python, and both are now provable. The true
twin of 1023.

A BOOLEAN operand keeps the `1`/`0` encoding, which is faithful because Python's
`True` IS `1`: `(a == a) or 5` is `True`, and `1` is what the model gives. The
ordinary `a == b or c == d` shape — both operands boolean — is unchanged, which
is why this repair leaves the corpus emissions alone apart from the handful of
sites that really did carry a non-boolean value.
"""
_ = 0  # anchor
#@ ensures \result == 5
#@ assigns \nothing
def f_or() -> int:
    x = 0 or 5
    return x


#@ ensures \result == 7
#@ assigns \nothing
def f_and() -> int:
    x = 3 and 7
    return x


#@ requires a == a
#@ ensures \result == 1
#@ assigns \nothing
def f_bool_left(a: int) -> int:
    x = (a == a) or 5
    return x
