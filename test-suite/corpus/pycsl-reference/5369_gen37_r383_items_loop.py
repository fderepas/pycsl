r"""Test 5369 -- gen #37 route #383 (expected FAIL): `for k, v in m.items(): {v}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union, Any, Iterator, Sequence

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(m: Dict[str, D]) -> int:
    for k, v in m.items():
        s = {v}
    return 1

if __name__ == "__main__":
    print(g({"a": D(1)}))
