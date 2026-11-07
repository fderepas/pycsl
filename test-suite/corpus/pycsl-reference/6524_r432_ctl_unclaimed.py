r"""Test 6524 -- route #432 (expected PASS): CONTROL: the same access without a `no_exception` claim is admitted. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Optional

def f(x: Optional[str]) -> int:
    return len(x.strip())
