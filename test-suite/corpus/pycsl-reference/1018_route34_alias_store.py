"""Test 1018 — ROUTE #34: an ALIAS then a store. `b = a` aliases in Python.

FALSE OF THE PROGRAM: the store through `b` changes `a[0]` to 9, so Python
returns 9. Proved `\result == 5` at c4233fed.

The emitted WhyML is `let b = a in b[0] <- 9`, which in Why3 mutates `a`
correctly — arrays are references there. The model of the STORE was never the
problem; the element fold answered the read before the store could matter.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    a = [5]
    b = a
    b[0] = 9
    return a[0]
