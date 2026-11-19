r"""Test 6547 -- route #437 (expected PASS): CONTROL: `sorted(List[Optional[int]])` under a claim that does not cover TypeError is admitted. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import List, Optional

#@ no_exception KeyError
def f(xs: List[Optional[int]]) -> int:
    ys = sorted(xs)
    return len(ys)
