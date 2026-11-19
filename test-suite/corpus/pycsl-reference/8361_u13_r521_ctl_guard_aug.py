r"""Test 8361 -- route #521 (control, expected PASS): guarded `t += v`; CPython never raises
"""
# pycsl-expected: PASS
from typing import Dict, List, Optional
from dataclasses import dataclass


#@ no_exception \all
def f(d: Dict[str, int]) -> int:
    v = d.get("k")
    t = 1
    if v is not None:
        t += v
    return t
