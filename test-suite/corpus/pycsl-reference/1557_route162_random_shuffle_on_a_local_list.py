r"""Test 1557 - ROUTE #162 (gen #29): `random.seed(0); random.shuffle(xs)` left the model's `xs` untouched and `xs[0] == 1` PROVED; CPython 5.
"""
# pycsl-expected: FAIL
import random
from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[int] = [1, 2, 3, 4, 5, 6, 7, 8]
    random.seed(0)
    random.shuffle(xs)
    return xs[0]

