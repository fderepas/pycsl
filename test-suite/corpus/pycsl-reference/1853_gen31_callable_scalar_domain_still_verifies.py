r"""Test 1853 — gen #31 CONTROL for 1852 (expected PASS): a scalar domain is untouched.

`Callable[[int], int]` — the admissible shape — verifies, so the refusal in 1852 is about
the collection DOMAIN and not a ban on `Callable` parameters.
"""
# pycsl-expected: PASS
from typing import Callable

_ = 0  # anchor


#@ ensures \result >= 0
#@ assigns \nothing
def apply(f: Callable[[int], int], x: int) -> int:
    return 0
