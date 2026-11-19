r"""Test 1924 — gen #36 (expected FAIL): ROUTE #230 — dict.get of a key whose stored value is None

The None that flows through a container (route #227's surviving carrier, backlog #65).
At 9aa13e5c this PROVED `\result == 3` under `#@ no_exception \all`; CPython raises TypeError.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Dict, List, Optional


#@ ensures \result == 3
#@ no_exception \all
#@ assigns \nothing
def f(k: int) -> int:
    d = {k: None}
    v = d.get(k)
    return v - v + 3
