r"""Test 6534 -- route #433 (expected PASS): CONTROL: `b"-".join(xs)`, `xs: List[bytes]` is admitted. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import List

#@ no_exception \all
def f(xs: List[bytes]) -> int:
    return len(b"-".join(xs))
