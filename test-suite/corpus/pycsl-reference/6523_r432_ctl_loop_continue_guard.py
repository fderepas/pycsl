r"""Test 6523 -- route #432 (expected PASS): CONTROL: `if x is None: continue` inside a loop is admitted. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import List, Optional

#@ no_exception \all
def f(xs: List[Optional[str]]) -> int:
    n = 0
    for x in xs:
        if x is None:
            continue
        n += len(x.strip())
    return n
