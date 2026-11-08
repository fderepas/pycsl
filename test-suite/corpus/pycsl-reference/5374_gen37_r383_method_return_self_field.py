r"""Test 5374 -- gen #37 route #383 (expected FAIL): `e = r.get(); {e}` with `get(self) -> D` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union, Any, Iterator, Sequence

@dataclass
class D:
    x: int

class R:
    def __init__(self, d: D) -> None:
        self.d = d
    #@ assigns \nothing
    def get(self) -> D:
        return self.d

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    e = r.get()
    s = {e}
    return 1

if __name__ == "__main__":
    print(g(R(D(1))))
