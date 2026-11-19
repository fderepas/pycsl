r"""Test 6546 -- route #437 (expected PASS): CONTROL: `sorted(List[int])`, `max(a, b)` / `min(a, b)` over ints is admitted. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import List

#@ no_exception \all
def f(xs: List[int], a: int, b: int) -> int:
    ys = sorted(xs)
    return len(ys) + max(a, b) - min(a, b)
