r"""Test 6535 -- route #433 (expected PASS): CONTROL: a join over `List[int]` without a `no_exception` claim is admitted. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import List

def f(xs: List[int]) -> int:
    return len("".join(xs))
