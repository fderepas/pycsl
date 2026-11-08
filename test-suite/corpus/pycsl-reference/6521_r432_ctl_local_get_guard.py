r"""Test 6521 -- route #432 (expected PASS): CONTROL: a guarded local from `d.get` is admitted. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Dict

#@ no_exception \all
def f(d: Dict[str, str]) -> int:
    v = d.get("a")
    if v is not None:
        return len(v.strip())
    return 0
