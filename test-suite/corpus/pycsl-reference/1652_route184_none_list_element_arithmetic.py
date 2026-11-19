r"""Test 1652 - ROUTE #184 (gen #29): the same `None` element used in arithmetic - `v = xs[0]; return v + 1` - PROVED `\result == 1` while CPython raises TypeError.
"""
# pycsl-expected: FAIL
from typing import List, Optional
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[Optional[int]] = [None]
    v = xs[0]
    return v + 1
