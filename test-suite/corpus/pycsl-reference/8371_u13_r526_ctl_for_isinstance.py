r"""Test 8371 -- route #526 (control, expected PASS): `for x in xs: if isinstance(x, int): t += x` over List[Optional[int]]; CPython never raises
"""
# pycsl-expected: PASS
from typing import Dict, List, Optional
from dataclasses import dataclass


#@ no_exception \all
def f(xs: List[Optional[int]]) -> int:
    t = 0
    for x in xs:
        if isinstance(x, int):
            t += x
    return t
