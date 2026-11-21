r"""Test 5376 -- gen #37 route #383 (expected FAIL): `d: T` (TypeVar), `{d}` in a file with an unhashable class (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union, Any, Iterator, Sequence

@dataclass
class D:
    x: int

from typing import TypeVar
T = TypeVar("T")

#@ no_exception \all
#@ ensures \result == 1
def g(d: T) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D(1)))
