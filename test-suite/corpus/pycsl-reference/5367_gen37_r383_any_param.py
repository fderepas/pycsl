r"""Test 5367 -- gen #37 route #383 (expected FAIL): `d: Any`, `{d}` in a file with an unhashable class (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union, Any

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(d: Any) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D(1)))
