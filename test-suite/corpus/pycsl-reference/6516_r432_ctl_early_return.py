r"""Test 6516 -- route #432 (expected PASS): CONTROL: `if x is None: return 0` narrows what follows is admitted. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Optional

#@ no_exception \all
def f(x: Optional[str]) -> int:
    if x is None:
        return 0
    return len(x.strip())
