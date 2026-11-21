r"""Test 6522 -- route #432 (expected PASS): CONTROL: a local rebound from a narrowed receiver's method is admitted. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Optional, Dict

#@ no_exception \all
def f(d: Dict[str, str], k: str) -> int:
    v = d.get(k)
    if v is None:
        return 0
    w = v.strip()
    return len(w.upper())
