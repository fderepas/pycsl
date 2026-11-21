r"""Test 5366 -- gen #37 route #383 (expected FAIL): `{r.get()}` with `get(self) -> D` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union, Any

@dataclass
class D:
    x: int

class R:
    def __init__(self) -> None:
        self.n = 1
    #@ assigns \nothing
    def get(self) -> D:
        return D(1)

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    s = {r.get()}
    return 1

if __name__ == "__main__":
    print(g(R()))
