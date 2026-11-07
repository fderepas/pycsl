r"""Test 1735 — WITNESS for `PYCSL-SEM-ASSIGNS`: an assigns REGION on a non-list variable.

`#@ assigns n[0..1]` where `n: int`. A range frame over a scalar is meaningless, and
accepting it would let a frame appear to cover storage that does not exist. Sibling: 1734
(a region naming an undefined variable).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires n >= 0
#@ assigns n[0..1]
def f(n: int) -> None:
    pass
