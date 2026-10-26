r"""Test 5370 -- gen #37 route #383 (expected FAIL): module alias `DL = List[D]`, `{ds[0]}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union, Any, Iterator, Sequence

@dataclass
class D:
    x: int

DL = List[D]

#@ no_exception \all
#@ requires \length(ds) >= 1
#@ ensures \result == 1
def g(ds: DL) -> int:
    s = {ds[0]}
    return 1

if __name__ == "__main__":
    print(g([D(1)]))
