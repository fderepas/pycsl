r"""Test 5372 -- gen #37 route #383 (expected FAIL): `{r.m.get(..)}` over a `Dict[str, D]` field (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union, Any, Iterator, Sequence

@dataclass
class D:
    x: int

class R:
    def __init__(self, m: Dict[str, D]) -> None:
        self.m = m

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    s = {r.m.get("a")}
    return 1

if __name__ == "__main__":
    print(g(R({"a": D(1)})))
