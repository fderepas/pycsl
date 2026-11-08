r"""Test 6520 -- route #432 (expected PASS): CONTROL: `x.strip() if x is not None else ..` narrows is admitted. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Optional

#@ no_exception \all
def f(x: Optional[str]) -> int:
    return len(x.strip()) if x is not None else 0
