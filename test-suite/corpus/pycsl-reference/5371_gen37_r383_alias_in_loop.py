r"""Test 5371 -- gen #37 route #383 (expected FAIL): `ds: List[DD]` (alias), `for d in ds: {d}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union, Any, Iterator, Sequence

@dataclass
class D:
    x: int

DD = D

#@ no_exception \all
#@ ensures \result == 1
def g(ds: List[DD]) -> int:
    for d in ds:
        s = {d}
    return 1

if __name__ == "__main__":
    print(g([D(1)]))
