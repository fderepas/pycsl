r"""Test 8366 -- route #524 (control, expected PASS): guarded `xss[0][0]` of List[List[Optional[int]]]; CPython never raises
"""
# pycsl-expected: PASS
from typing import Dict, List, Optional
from dataclasses import dataclass


#@ requires len(xss) >= 1 and len(xss[0]) >= 1
#@ no_exception \all
def f(xss: List[List[Optional[int]]]) -> int:
    v = xss[0][0]
    if v is not None:
        return v + 1
    return 0
