r"""Test 1929 — gen #36 (expected PASS): ROUTE #230 — CONTROL: the same dict read under an is-not-None guard verifies

The None that flows through a container (route #227's surviving carrier, backlog #65).
At 9aa13e5c this PROVED `\result == 3` under `#@ no_exception \all`; CPython raises TypeError.
"""
# pycsl-expected: PASS
_ = 0  # anchor
from typing import Dict, List, Optional


#@ ensures \result == 3
#@ no_exception \all
#@ assigns \nothing
def f(k: int) -> int:
    d: Dict[int, Optional[int]] = {}
    d[k] = None
    v = d[k]
    if v is not None:
        return v - v + 3
    return 3
