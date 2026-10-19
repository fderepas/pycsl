r"""Test 3087 — route #279 (expected FAIL): `b = xs; b += [1]` on a list PARAMETER grows the caller's
list; before the repair the emission was ill-typed (fail-closed by accident); now refused by name.
CPython: the caller sees length 2.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires len(xs) == 1
#@ ensures len(xs) == 1
#@ assigns \nothing
def f(xs: List[int]) -> None:
    b = xs
    b += [1]


if __name__ == "__main__":
    x = [0]
    f(x)
    assert len(x) == 2
