r"""Test 5361 -- gen #37 route #383 (expected FAIL): `{*ds}` over `ds: List[D]` (D eq-dataclass) (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import List

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(ds: List[D]) -> int:
    s = {*ds}
    return 1

if __name__ == "__main__":
    print(g([D(1)]))
