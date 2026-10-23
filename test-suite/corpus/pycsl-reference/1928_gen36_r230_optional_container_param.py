r"""Test 1928 — gen #36 (expected FAIL): ROUTE #230 — a parameter declared Dict[int, Optional[int]] (the caller stored the None)

The None that flows through a container (route #227's surviving carrier, backlog #65).
At 9aa13e5c this PROVED `\result == 3` under `#@ no_exception \all`; CPython raises TypeError.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Dict, List, Optional


#@ requires k in d
#@ ensures \result == 3
#@ no_exception \all
#@ assigns \nothing
def f(d: Dict[int, Optional[int]], k: int) -> int:
    v = d[k]
    return v - v + 3
