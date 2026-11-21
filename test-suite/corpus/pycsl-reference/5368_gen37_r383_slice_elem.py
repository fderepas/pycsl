r"""Test 5368 -- gen #37 route #383 (expected FAIL): `t = ds[0:1]; {t[0]}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union, Any

@dataclass
class D:
    x: int

#@ no_exception \all
#@ requires \length(ds) >= 1
#@ ensures \result == 1
def g(ds: List[D]) -> int:
    t = ds[0:1]
    s = {t[0]}
    return 1

if __name__ == "__main__":
    print(g([D(1)]))
