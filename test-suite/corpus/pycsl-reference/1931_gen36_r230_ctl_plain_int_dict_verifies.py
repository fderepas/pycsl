r"""Test 1931 — gen #36 (expected PASS): ROUTE #230 — CONTROL: a plain Dict[int, int] read is not fenced

The None that flows through a container (route #227's surviving carrier, backlog #65).
At 9aa13e5c this PROVED `\result == 3` under `#@ no_exception \all`; CPython raises TypeError.
"""
# pycsl-expected: PASS
_ = 0  # anchor
from typing import Dict, List, Optional


#@ requires k in d
#@ ensures \result == 3
#@ no_exception \all
#@ assigns \nothing
def f(d: Dict[int, int], k: int) -> int:
    v = d[k]
    return v - v + 3
