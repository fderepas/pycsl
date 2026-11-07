r"""Test 6515 -- route #432 (expected PASS): CONTROL: `if x is not None:` narrows is admitted. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Optional

#@ no_exception \all
def f(x: Optional[str]) -> int:
    if x is not None:
        return len(x.strip())
    return 0
