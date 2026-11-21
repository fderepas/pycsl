r"""Test 1930 — gen #36 (expected PASS): ROUTE #230 — CONTROL: dict.get with an int default is not fenced

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
    d: Dict[int, int] = {}
    v = d.get(k, 0)
    return v - v + 3
