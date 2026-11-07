r"""Test 5373 -- gen #37 route #383 (expected FAIL): `{r.d}` with a field stored from `d: Any` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union, Any, Iterator, Sequence

@dataclass
class D:
    x: int

class R:
    def __init__(self, d: Any) -> None:
        self.d = d

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    s = {r.d}
    return 1

if __name__ == "__main__":
    print(g(R(D(1))))
