r"""Test 8364 -- route #522 (control, expected PASS): guarded `r.d.get("k")` and `r.d.get("j", 0) + 1`; CPython never raises
"""
# pycsl-expected: PASS
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class R:
    d: Dict[str, int]

#@ no_exception \all
def f(r: R) -> int:
    v = r.d.get("k")
    if v is not None:
        return v + 1
    return r.d.get("j", 0) + 1
