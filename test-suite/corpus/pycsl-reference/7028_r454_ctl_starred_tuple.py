r"""Test 7028 -- route #454 (expected PASS): CONTROL -- `(*xs, 1)` with `xs: Tuple[int, int]` (derived iterable); PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import List, Tuple
#@ no_exception \all
def f(xs: Tuple[int, int]) -> int:
    t = (*xs, 1)
    return len(t)
